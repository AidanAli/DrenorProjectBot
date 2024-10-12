import discord
from discord.ext import commands
import requests
import xmltodict
import json
import base64

from main import discord_hook


# Load configuration




class AzerothCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='register', help='Registers a new account in AzerothCore')
    async def register(self, ctx, username: str, password: str, email: str):
        # Construct the GM command
        REGISTER_USER = f'account create {username} {password}'

        # SOAP Request XML
        xml_request = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:AC">
           <soapenv:Header/>
           <soapenv:Body>
              <urn:executeCommand>
                 <command>{REGISTER_USER}</command>
                 <username>master</username>
                 <password>master</password>
              </urn:executeCommand>
           </soapenv:Body>
        </soapenv:Envelope>
        """

        # Authorization Header
        auth = base64.b64encode(b'master:master').decode('utf-8')

        # SOAP API request headers
        headers = {
            'Content-Type': 'text/xml',
            'Authorization': f'Basic {auth}'
        }

        try:
            # Send SOAP request to AzerothCore
            response = requests.post(f'http://127.0.0.1:7878', data=xml_request, headers=headers)
            response.raise_for_status()
            soap_data = response.text

            # Parse the SOAP response XML
            result = xmltodict.parse(soap_data)

            # Send the entire parsed response to Discord WebHook
            formatted_response = f"**SOAP Response**\n```json\n{json.dumps(result, indent=2)}\n```\n**Email:** {email}"
            requests.post(discord_hook, json={"content": formatted_response})

            # Send a success message in the Discord channel
            await ctx.send(f"Account creation request for {username} has been sent successfully!")

        except requests.exceptions.RequestException as e:
            error_message = f'Error executing SOAP command: {str(e)}'
            print(error_message)

            # Send error to Discord WebHook
            formatted_error = f"**Error executing SOAP command**\n```\n{str(e)}\n```\n**Email:** {email}"
            requests.post(discord_hook, json={"content": formatted_error})

            # Send error message in the Discord channel
            await ctx.send(f"Failed to create account for {username}. Please check the logs.")


# Setup the cog
async def setup(bot):
    await bot.add_cog(AzerothCore(bot))
