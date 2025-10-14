from core.schema_generator import generate_tool_schemas

class MockAgent:
    """A mock agent for testing schema generation."""
    tools = ["get_weather", "get_stock_price"]

    def get_weather(self, city: str, unit: str = "celsius") -> str:
        """
        Gets the current weather for a specified city.

        Args:
            city: The name of the city.
            unit: The temperature unit (celsius or fahrenheit).
        """
        return "Sunny"

    def get_stock_price(self, symbol: str) -> float:
        """
        Gets the current stock price for a given symbol.

        Args:
            symbol: The stock ticker symbol.
        """
        return 150.75

    def unused_method(self):
        """This method should not be included in the schema."""
        pass

def test_generate_tool_schemas():
    """
    Tests that the schema generator correctly introspects an agent's methods
    and produces valid OpenAI tool schemas.
    """
    mock_agent = MockAgent()
    schemas = generate_tool_schemas(mock_agent)

    assert len(schemas) == 2, "Should only generate schemas for tools listed in agent.tools"

    # Test the schema for the 'get_weather' method
    weather_schema = next((s for s in schemas if s["function"]["name"] == "get_weather"), None)
    assert weather_schema is not None
    assert weather_schema["function"]["description"] == "Gets the current weather for a specified city."

    properties = weather_schema["function"]["parameters"]["properties"]
    assert properties["city"]["type"] == "string"
    assert properties["unit"]["type"] == "string"

    required = weather_schema["function"]["parameters"]["required"]
    assert "city" in required
    assert "unit" not in required # 'unit' has a default value, so it's not required

    # Test the schema for the 'get_stock_price' method
    stock_schema = next((s for s in schemas if s["function"]["name"] == "get_stock_price"), None)
    assert stock_schema is not None
    properties = stock_schema["function"]["parameters"]["properties"]
    assert properties["symbol"]["type"] == "string"
    required = stock_schema["function"]["parameters"]["required"]
    assert "symbol" in required

