"""
Tests for the HydrationCalculator class.
"""

import unittest
from unittest.mock import patch, MagicMock
from .hydration_calculator import HydrationCalculator

class TestHydrationCalculator(unittest.TestCase):
    """Test cases for HydrationCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = HydrationCalculator()
    
    def test_temperature_adjustment_hot(self):
        """Test temperature adjustment for hot weather."""
        # Test temperature above 25°C
        adjustment = self.calculator.calculate_temperature_adjustment(30)
        self.assertEqual(adjustment, 200)  # (30-25)/5 * 200 = 200
        
        adjustment = self.calculator.calculate_temperature_adjustment(35)
        self.assertEqual(adjustment, 400)  # (35-25)/5 * 200 = 400
    
    def test_temperature_adjustment_normal(self):
        """Test temperature adjustment for normal weather."""
        # Test temperature between 15-25°C
        adjustment = self.calculator.calculate_temperature_adjustment(20)
        self.assertEqual(adjustment, 0)  # No adjustment for normal temperature
        
        adjustment = self.calculator.calculate_temperature_adjustment(15)
        self.assertEqual(adjustment, 0)
        
        adjustment = self.calculator.calculate_temperature_adjustment(25)
        self.assertEqual(adjustment, 0)
    
    def test_temperature_adjustment_cold(self):
        """Test temperature adjustment for cold weather."""
        # Test temperature below 15°C
        adjustment = self.calculator.calculate_temperature_adjustment(10)
        self.assertEqual(adjustment, -100)  # (10-15)/5 * 100 = -100
        
        adjustment = self.calculator.calculate_temperature_adjustment(5)
        self.assertEqual(adjustment, -200)  # (5-15)/5 * 100 = -200
        
        # Test minimum adjustment
        adjustment = self.calculator.calculate_temperature_adjustment(-10)
        self.assertEqual(adjustment, -500)  # Minimum adjustment is -500
    
    def test_humidity_adjustment_high(self):
        """Test humidity adjustment for high humidity."""
        adjustment = self.calculator.calculate_humidity_adjustment(80)
        self.assertEqual(adjustment, 100)
    
    def test_humidity_adjustment_normal(self):
        """Test humidity adjustment for normal humidity."""
        adjustment = self.calculator.calculate_humidity_adjustment(50)
        self.assertEqual(adjustment, 0)
    
    def test_humidity_adjustment_low(self):
        """Test humidity adjustment for low humidity."""
        adjustment = self.calculator.calculate_humidity_adjustment(30)
        self.assertEqual(adjustment, 50)
    
    def test_activity_adjustment(self):
        """Test activity adjustment for different activity levels."""
        adjustment = self.calculator.calculate_activity_adjustment('high')
        self.assertEqual(adjustment, 300)
        
        adjustment = self.calculator.calculate_activity_adjustment('moderate')
        self.assertEqual(adjustment, 150)
        
        adjustment = self.calculator.calculate_activity_adjustment('low')
        self.assertEqual(adjustment, 0)
    
    @patch('smart_hydration.hydration_calculator.WeatherAPI')
    def test_get_recommendation(self, mock_weather_api):
        """Test get_recommendation method."""
        # Mock WeatherAPI methods
        mock_instance = mock_weather_api.return_value
        mock_instance.get_temperature.return_value = 30
        mock_instance.get_humidity.return_value = 80
        mock_instance.get_weather_condition.return_value = 'clear sky'
        
        # Create calculator with mocked API
        calculator = HydrationCalculator()
        
        # Test recommendation
        recommendation = calculator.get_recommendation(city='Test City')
        
        # Verify results
        self.assertEqual(recommendation['base'], 2000)
        self.assertEqual(recommendation['temperature'], 30)
        self.assertEqual(recommendation['humidity'], 80)
        self.assertEqual(recommendation['weather_condition'], 'clear sky')
        self.assertEqual(recommendation['temp_adjustment'], 200)
        self.assertEqual(recommendation['humidity_adjustment'], 100)
        self.assertEqual(recommendation['activity_adjustment'], 0)
        self.assertEqual(recommendation['total'], 2300)
        self.assertIn('hot', recommendation['explanation'].lower())
        self.assertIn('humidity', recommendation['explanation'].lower())
    
    def test_minimum_recommendation(self):
        """Test that recommendation never goes below 2000ml."""
        # Create a recommendation with negative adjustments
        with patch.object(self.calculator, 'calculate_temperature_adjustment', return_value=-500):
            with patch.object(self.calculator, 'calculate_humidity_adjustment', return_value=0):
                recommendation = self.calculator.get_recommendation(base_hydration=2000)
                self.assertEqual(recommendation['total'], 2000)  # Should not go below 2000ml

if __name__ == '__main__':
    unittest.main()
