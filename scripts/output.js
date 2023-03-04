function handler (data, serverless, options) {
  /**
  * Reference: https://www.serverless.com/plugins/serverless-stack-output
  * Handles the stack output.
  */
  data.LoginHostedUIURL = "https://"
        + data.CognitoUserPoolDomain
        + ".auth.us-east-1.amazoncognito.com/login?response_type=token"
        + "&client_id=" + data.CognitoUserPoolClientId
        + "&redirect_uri=" + data.CallbackURL;

  console.log('Received Stack Output', data)
}

module.exports = { handler }