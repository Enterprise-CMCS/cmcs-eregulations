import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm";

/**
 * Fetches a parameter value from AWS Systems Manager (SSM) Parameter Store with error handling.
 * @param path - The SSM parameter path.
 * @returns Promise<string> - The decrypted parameter value.
 * @throws Error - If the parameter is not found or if access is denied.
 */
export async function getParameterValue(path: string): Promise<string> {
    if (!path) {
        throw new Error("Parameter path is required");
    }

    const ssm = new SSMClient({
        maxAttempts: 3, // Retry up to 3 times
    });

    try {
        const response = await ssm.send(new GetParameterCommand({
            Name: path,
            WithDecryption: true,
        }));

        if (!response.Parameter || !response.Parameter.Value) {
            throw new Error(`Parameter not found or has no value: ${path}`);
        }

        return response.Parameter.Value;
    } catch (error) {
        if (error instanceof Error) {
            // Handle specific AWS SDK error names
            if (error.name === "ParameterNotFound") {
                throw new Error(`Parameter not found: ${path}`);
            }
            if (error.name === "AccessDeniedException") {
                throw new Error(`Access denied to parameter: ${path}`);
            }

            // Re-throw with additional context for other errors
            throw new Error(`Failed to fetch parameter ${path}: ${error.message}`);
        } else {
            // Handle non-Error exceptions (edge case)
            throw new Error(`Unexpected error fetching parameter ${path}`);
        }
    }
}
