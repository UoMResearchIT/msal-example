# Example use of MSAL to authenticate with Microsoft Graph API

This example app gets an access token to use the 
[Microsoft Graph API](https://docs.microsoft.com/en-us/graph/use-the-api) using the Microsoft Authentication Library 
[MSAL](https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-overview).

The example uses the device flow method to get an access token. This could easily be switched for a different token
acquisition method.

The example uses a local cache to cache the access token. This means that authentication is only required on the first
run of the application. Although the access token is only valid for an hour, a refresh token is also stored which is
valid for 90 days. If the access token has expired, the refresh token is used silently to update the access token.

## Security Warning
This example locally caches the API access tokens in plain text. This is insecure and so unsuitable for a 
production application. You will likely want to encrypt the local token store. One possible way to do this is to use 
the using the [MSAL Python extensions](https://github.com/AzureAD/microsoft-authentication-extensions-for-python) 
package.
