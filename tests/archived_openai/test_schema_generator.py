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

def test_generate_tool_schemas_is_flat():
    """
    Tests that the schema generator produces a flat structure for function tools.
    """
    mock_agent = MockAgent()
    schemas = generate_tool_schemas(mock_agent)

    assert len(schemas) == 2

    weather_schema = next((s for s in schemas if s["name"] == "get_weather"), None)
    assert weather_schema is not None
    
    # Assert that the main keys are at the top level, not nested.
    assert weather_schema["type"] == "function"
    assert weather_schema["name"] == "get_weather"
    assert "parameters" in weather_schema

    properties = weather_schema["parameters"]["properties"]
    assert properties["city"]["description"] == "The name of the city."

