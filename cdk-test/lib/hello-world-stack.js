"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HelloWorldStack = void 0;
const cdk = require("aws-cdk-lib");
// Lambda L2 construct
const lambda = require("aws-cdk-lib/aws-lambda");
// API Gateway L2 construct
const apigateway = require("aws-cdk-lib/aws-apigateway");
class HelloWorldStack extends cdk.Stack {
    constructor(scope, id, stage, props) {
        super(scope, id, props);
        const helloWorldLambda = new lambda.Function(this, `cmcs-eregs-${stage}-HelloWorldLambda`, {
            runtime: lambda.Runtime.NODEJS_20_X,
            handler: 'hello.handler',
            code: lambda.Code.fromAsset('lambda'),
        });
        const apiGateway = new apigateway.LambdaRestApi(this, `cmcs-eregs-${stage}-HelloWorldAPI`, {
            handler: helloWorldLambda,
            proxy: false,
        });
        const helloResource = apiGateway.root.addResource('hello');
        helloResource.addMethod('GET');
    }
}
exports.HelloWorldStack = HelloWorldStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiaGVsbG8td29ybGQtc3RhY2suanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJoZWxsby13b3JsZC1zdGFjay50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFBQSxtQ0FBbUM7QUFHbkMsc0JBQXNCO0FBQ3RCLGlEQUFpRDtBQUVqRCwyQkFBMkI7QUFDM0IseURBQXlEO0FBRXpELE1BQWEsZUFBZ0IsU0FBUSxHQUFHLENBQUMsS0FBSztJQUM1QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQWEsRUFBRSxLQUFzQjtRQUM3RSxLQUFLLENBQUMsS0FBSyxFQUFFLEVBQUUsRUFBRSxLQUFLLENBQUMsQ0FBQztRQUV4QixNQUFNLGdCQUFnQixHQUFHLElBQUksTUFBTSxDQUFDLFFBQVEsQ0FBQyxJQUFJLEVBQUUsY0FBYyxLQUFLLG1CQUFtQixFQUFFO1lBQ3pGLE9BQU8sRUFBRSxNQUFNLENBQUMsT0FBTyxDQUFDLFdBQVc7WUFDbkMsT0FBTyxFQUFFLGVBQWU7WUFDeEIsSUFBSSxFQUFFLE1BQU0sQ0FBQyxJQUFJLENBQUMsU0FBUyxDQUFDLFFBQVEsQ0FBQztTQUN0QyxDQUFDLENBQUM7UUFFSCxNQUFNLFVBQVUsR0FBRyxJQUFJLFVBQVUsQ0FBQyxhQUFhLENBQUMsSUFBSSxFQUFFLGNBQWMsS0FBSyxnQkFBZ0IsRUFBRTtZQUN6RixPQUFPLEVBQUUsZ0JBQWdCO1lBQ3pCLEtBQUssRUFBRSxLQUFLO1NBQ2IsQ0FBQyxDQUFDO1FBRUgsTUFBTSxhQUFhLEdBQUcsVUFBVSxDQUFDLElBQUksQ0FBQyxXQUFXLENBQUMsT0FBTyxDQUFDLENBQUM7UUFDM0QsYUFBYSxDQUFDLFNBQVMsQ0FBQyxLQUFLLENBQUMsQ0FBQztJQUNqQyxDQUFDO0NBQ0Y7QUFsQkQsMENBa0JDIiwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcbmltcG9ydCB7IENvbnN0cnVjdCB9IGZyb20gJ2NvbnN0cnVjdHMnO1xuXG4vLyBMYW1iZGEgTDIgY29uc3RydWN0XG5pbXBvcnQgKiBhcyBsYW1iZGEgZnJvbSAnYXdzLWNkay1saWIvYXdzLWxhbWJkYSc7XG5cbi8vIEFQSSBHYXRld2F5IEwyIGNvbnN0cnVjdFxuaW1wb3J0ICogYXMgYXBpZ2F0ZXdheSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtYXBpZ2F0ZXdheSc7XG5cbmV4cG9ydCBjbGFzcyBIZWxsb1dvcmxkU3RhY2sgZXh0ZW5kcyBjZGsuU3RhY2sge1xuICBjb25zdHJ1Y3RvcihzY29wZTogQ29uc3RydWN0LCBpZDogc3RyaW5nLCBzdGFnZTogc3RyaW5nLCBwcm9wcz86IGNkay5TdGFja1Byb3BzKSB7XG4gICAgc3VwZXIoc2NvcGUsIGlkLCBwcm9wcyk7XG5cbiAgICBjb25zdCBoZWxsb1dvcmxkTGFtYmRhID0gbmV3IGxhbWJkYS5GdW5jdGlvbih0aGlzLCBgY21jcy1lcmVncy0ke3N0YWdlfS1IZWxsb1dvcmxkTGFtYmRhYCwge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuTk9ERUpTXzIwX1gsXG4gICAgICBoYW5kbGVyOiAnaGVsbG8uaGFuZGxlcicsXG4gICAgICBjb2RlOiBsYW1iZGEuQ29kZS5mcm9tQXNzZXQoJ2xhbWJkYScpLFxuICAgIH0pO1xuXG4gICAgY29uc3QgYXBpR2F0ZXdheSA9IG5ldyBhcGlnYXRld2F5LkxhbWJkYVJlc3RBcGkodGhpcywgYGNtY3MtZXJlZ3MtJHtzdGFnZX0tSGVsbG9Xb3JsZEFQSWAsIHtcbiAgICAgIGhhbmRsZXI6IGhlbGxvV29ybGRMYW1iZGEsXG4gICAgICBwcm94eTogZmFsc2UsXG4gICAgfSk7XG5cbiAgICBjb25zdCBoZWxsb1Jlc291cmNlID0gYXBpR2F0ZXdheS5yb290LmFkZFJlc291cmNlKCdoZWxsbycpO1xuICAgIGhlbGxvUmVzb3VyY2UuYWRkTWV0aG9kKCdHRVQnKTtcbiAgfVxufVxuIl19