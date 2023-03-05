# JSON Schema Validation for AWS API Gateway API

This project includes JSON Schema validators for the AWS API Gateway API.  
This reduces unnecessary calls to the backend, saving cost and making the app more efficient, and lets me focus on the validation specific to the business logic in my application.  

These validators are important for ensuring that requests to the API match a predefined schema, helping to improve the reliability and security of the API.   

By validating the input data, I can ensure that requests are well-formed and contain all the required fields, preventing common errors and potential security vulnerabilities. 

The validators are also easily configurable and can be extended to support custom validation rules as needed. Using JSON Schema validators is a best practice for API development and helps to ensure a more robust and secure API.


## Reference docs:

- [API Gateway request validation](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-request-validation.html)
- [JSON Schema website](https://json-schema.org/)
- [Understanding JSON Schema learning resource](https://json-schema.org/understanding-json-schema/index.html)
- [Validator to test schemas](https://www.jsonschemavalidator.net/)