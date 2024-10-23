// parameter.ts
import { SSM } from 'aws-sdk';

/**
* Fetches parameter from SSM with error handling
* @param path - SSM parameter path
* @returns Promise with parameter value
* @throws Error if parameter not found or access denied
*/
export async function getParameterValue(path: string): Promise<string> {
 if (!path) {
   throw new Error('Parameter path is required');
 }

 try {
   const ssm = new SSM();
   const response = await ssm.getParameter({
     Name: path,
     WithDecryption: true
   }).promise();

   // Check if parameter exists and has value
   if (!response.Parameter) {
     throw new Error(`Parameter not found: ${path}`);
   }

   if (!response.Parameter.Value) {
     throw new Error(`Parameter exists but has no value: ${path}`);
   }

   return response.Parameter.Value;

 } catch (error) {
   if (error instanceof Error) {
     // AWS SDK specific errors
     if (error.name === 'ParameterNotFound') {
       throw new Error(`Parameter not found: ${path}`);
     }
     if (error.name === 'AccessDeniedException') {
       throw new Error(`Access denied to parameter: ${path}`);
     }
     
     // Re-throw with context
     throw new Error(`Failed to fetch parameter ${path}: ${error.message}`);
   }
   
   // Unknown error type
   throw new Error(`Unexpected error fetching parameter ${path}`);
 }
}
