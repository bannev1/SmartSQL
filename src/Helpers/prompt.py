from openai import AzureOpenAI


class Prompter:
	def __init__(self, APIkeys: dict[str]) -> None:
		"""
		Helper class to manage prompting given API keys

		Args:
			APIkeys (dict[str]): Equivalent of .env in dictionary form, see README.md for more information/layout example
		
		### Example Structure of `APIkeys`:

		```
		{
			"AZURE_OPENAI_API_KEY" : "API Key",
			"AZURE_OPENAI_ENDPOINT" : "OpenAI Endpoint",
			"AZURE_OPENAI_API_VERSION" : "API Version",
			"AZURE_OPENAI_DEPLOYMENT_NAME" : "AI Model",
			"AZURE_AI_KEY" : "Azure AI API Key",
			"AZURE_AI_ENDPOINT" : "Azure AI Endpoint"
		}
		```
		"""

		# Set up client
		self.client = AzureOpenAI(
			api_key= APIkeys['AZURE_OPENAI_API_KEY'],
			api_version= APIkeys['AZURE_OPENAI_API_VERSION'],
			azure_endpoint= APIkeys['AZURE_OPENAI_ENDPOINT']
		)

		self.deploymentName = APIkeys['AZURE_OPENAI_DEPLOYMENT_NAME']

		self.backlog = []


	def prompt(self, basePrompt: str, query: str, updateBacklog: bool = True, **kwargs) -> str:
		"""
		Helper method to prompt the query to the AI model. Returns result as a string.

		Args:
			basePrompt (str): System prompt
			query (str): User prompt
			updateBacklog (bool): If need to add record to backlog
			**kwargs: Any arguments needed to pass into .create() for AI
		"""

		# Prompt GPT
		response = self.client.chat.completions.create(
			model = self.deploymentName,
			messages = [
					{
						"role": "system", 
						"content": basePrompt,
					},
					{
						"role": "user", 
						"content": query
					}
				],
			**kwargs
		)

		result = response.choices[0].message.content

		# Update backlog
		if updateBacklog:
			self.backlog.append(result)

		return result
	
	def clearBacklog(self) -> None:
		"""
		Clear backlog list
		"""

		self.backlog = []
