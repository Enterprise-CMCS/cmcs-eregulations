import os
import logging
import io
import json

from .exceptions import ExtractorException, ExtractorInitException
from .extractor import Extractor

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


class PdfExtractor(Extractor):
    file_types = ("pdf",)

    def __init__(self, file_type: str, config: dict, *args, **kwargs):
        super().__init__(file_type, config)
        self.textract_client = self._get_boto3_client("textract")
        self.s3_client = self._get_boto3_client("s3")
        self.sqs_client = self._get_boto3_client("sqs")
        self.bucket = os.environ.get("TEXTRACT_BUCKET")
        if not self.bucket:
            raise ExtractorInitException("TEXTRACT_BUCKET environment variable is not set.")
        self.queue_url = os.environ.get("TEXT_EXTRACTOR_QUEUE_URL")
        if not self.queue_url:
            logger.warning(
                "TEXT_EXTRACTOR_QUEUE_URL environment variable is not set. "
                "Textract jobs will be processed synchronously, which may lead to timeouts for large files."
            )

    def _start_text_extraction(self, file: bytes, resource_id: int) -> str:
        # Upload the PDF file to the temporary storage bucket
        try:
            self.s3_client.upload_fileobj(io.BytesIO(file), self.bucket, f"{resource_id}.pdf")
            logger.info("Uploaded PDF file to S3 bucket \"%s\".", self.bucket)
        except Exception as e:
            raise ExtractorException(f"failed to upload PDF file to S3: {str(e)}")

        # Call Textract to analyze the document
        try:
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={
                    "S3Object": {
                        "Bucket": self.bucket,
                        "Name": f"{resource_id}.pdf",
                    },
                },
                OutputConfig={
                    "S3Bucket": self.bucket,
                    "S3Prefix": f"textract-results/{resource_id}",
                },
            )
            logger.info("Started document text detection job with ID \"%s\".", response["JobId"])
            return response["JobId"]
        except Exception as e:
            raise ExtractorException(f"failed to start Textract job: {str(e)}")

    def _cleanup_s3(self, resource_id: int):
        # Clean up the S3 bucket by deleting the uploaded PDF and any Textract results
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=f"{resource_id}.pdf")
            logger.info("Deleted PDF file from S3 bucket \"%s\".", self.bucket)
            self.s3_client.delete_objects(
                Bucket=self.bucket,
                Delete={
                    "Objects": [
                        {"Key": f"textract-results/{resource_id}/{obj['Key']}"}
                        for obj in self.s3_client.list_objects_v2(
                            Bucket=self.bucket,
                            Prefix=f"textract-results/{resource_id}"
                        ).get("Contents", [])
                    ]
                }
            )
            logger.info("Deleted Textract results from S3 bucket \"%s\".", self.bucket)
        except Exception as e:
            # Log the error but do not raise it, as this is a cleanup operation
            logger.error(f"Failed to clean up S3 bucket: {str(e)}")

    def _extract(self, file: bytes) -> str:
        resource_id = self.config["id"]

        if "job_id" in self.config:
            job_id = self.config["job_id"]
            logger.info("Using existing Textract job ID \"%s\" from config.", job_id)

            # Check the job's status in Textract
            try:
                response = self.textract_client.get_document_text_detection(JobId=job_id)
                job_status = response["JobStatus"]
            except Exception as e:
                # If the job ID is not found or any other error occurs, raise an exception
                # It will be handled by the SQS message processing logic, including retrying if possible
                raise ExtractorException(f"failed to get Textract job status: {str(e)}")

            # Handle all possible Textract job statuses
            if job_status == "SUCCEEDED" or job_status == "PARTIAL_SUCCESS":
                logger.info("Textract job \"%s\" completed successfully.", job_id)
                # Process the results and return the extracted text
                text = ""
                for item in response["Blocks"]:
                    if item["BlockType"] == "LINE":
                        text += item["Text"] + " "
                # Clean up the S3 bucket after successful extraction
                logger.info("Attempting to clean up S3 bucket after successful extraction.")
                self._cleanup_s3(resource_id)
                return text
            elif job_status == "FAILED":
                status_message = response.get("StatusMessage", "No message provided")
                raise ExtractorException(f"Textract job \"{job_id}\" failed: {status_message}")
            elif job_status == "IN_PROGRESS":
                logger.info("Textract job \"%s\" is still in progress. Will check again later.", job_id)
            else:
                raise ExtractorException(f"Textract job \"{job_id}\" is in an unexpected state: {job_status}")
        else:
            job_id = self._start_text_extraction(file, resource_id)
            self.config["job_id"] = job_id  # For synchronous processing

        if self.queue_url:
            # Push a new job to the SQS queue, and we'll check Textract's status later
            try:
                self.sqs_client.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=json.dumps({
                        "job_id": job_id,
                        "file_type": self.file_type,
                        **self.config,  # Include the original config in the message body
                    }),
                    MessageGroupId=f"textract:{resource_id}",  # Use resource_id as the new group ID to allow parallel processing
                )
                logger.info("Pushed Textract job ID \"%s\" to SQS queue \"%s\".", job_id, self.queue_url)
                return None  # No text is returned immediately; the job will be processed asynchronously
            except Exception as e:
                raise ExtractorException(f"failed to push job to SQS: {str(e)}")

        # If no queue URL is set, we will process the job synchronously
        return self._extract(None)
