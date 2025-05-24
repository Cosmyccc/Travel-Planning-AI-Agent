from llama_index.core.tools.tool_spec.base import BaseToolSpec
import requests
import pandas as pd
from datetime import date, datetime
from typing import Dict, Optional, List, Union
import re
from dateutil import parser
import os
from dotenv import load_dotenv

load_dotenv()

class TravelTool(BaseToolSpec):
    spec_functions = ["search_flights", "search_buses", "search_trains", "search_cabs", 
                     "book_transport", "cancel_booking", "get_booking_status"]

    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        # print(self.rapidapi_key)
        if not self.rapidapi_key or not self.rapidapi_key:
            raise ValueError("API keys not found in environment variables")
        
        # For flight searches (TripAdvisor/RapidAPI)
        self.flight_base_url = "https://tripadvisor-com1.p.rapidapi.com/flights/search-one-way"
        self.flight_headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "tripadvisor-com1.p.rapidapi.com"
        }

    def _make_request(self, endpoint: str, params: Dict, api_type: str = "transport") -> Union[Dict, str]:
        """Improved request handler with API type selection"""
        try:
            base_url = self.flight_base_url if api_type == "flight" else self.transport_base_url
            headers = self.flight_headers if api_type == "flight" else self.transport_headers
            
            response = requests.get(
                f"{base_url}/{endpoint}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"API request failed: {str(e)} (Status: {e.response.status_code if hasattr(e, 'response') else 'N/A'})"

    def search_flights(self, origin: str, destination: str, date: str) -> Union[pd.DataFrame, str]:
        """
        Flight-only search with enhanced error handling
        Returns either:
        - DataFrame of flight options
        - String error message
        """
        try:
            # Validate date format
            try:
                departure_date = parser.parse(date).date()
                if departure_date < datetime.now().date():
                    return "Error: Date must be in the future (YYYY-MM-DD format)"
            except ValueError:
                return "Error: Invalid date format. Please use YYYY-MM-DD"

            # Prepare API request
            params = {
                "from": origin,
                "to": destination,
                "date": date,
                "adults": 1,
                "currency": "USD"
            }

            # Make API call
            result = self._make_request("search-one-way", params, api_type="flight")
            
            # Handle API errors
            if isinstance(result, str):
                if "403" in result:
                    return "Error 403: API access denied. Please check your API credentials and subscription."
                return f"API Error: {result}"

            # Process successful response
            flights = []
            for flight in result.get("data", []):
                flights.append({
                    "airline": flight.get("operating_carrier", {}).get("display_name", "Unknown"),
                    "flight_no": flight.get("flight_number", "N/A"),
                    "departure": flight.get("departure_time", "N/A"),
                    "arrival": flight.get("arrival_time", "N/A"),
                    "duration": flight.get("duration", "N/A"),
                    "price": flight.get("price", {}).get("amount", "Contact for pricing")
                })

            return pd.DataFrame(flights) if flights else "No flights found for this route"

        except Exception as e:
            return f"System error: {str(e)}. Please try again later."

    def search_buses(self, origin: str, destination: str, date: str) -> Union[pd.DataFrame, str]:
        """
        Search for bus routes between two locations on a specific date
        
        Args:
            origin: Departure location
            destination: Arrival location
            date: Travel date (YYYY-MM-DD format)
            
        Returns:
            DataFrame with bus options or error message
        """
        try:
            # Validate date format
            departure_date = parser.parse(date).date()
            if departure_date < datetime.now().date():
                return "Error: Date must be in the future"
                
            params = {
                "from": origin,
                "to": destination,
                "date": date,
                "transport_types": "bus",
                "limit": 10
            }
            
            result = self._make_request("connections", params)
            if isinstance(result, str):
                return result
                
            buses = []
            for connection in result.get("connections", []):
                buses.append({
                    "departure": connection.get("from", {}).get("departure"),
                    "arrival": connection.get("to", {}).get("arrival"),
                    "duration": connection.get("duration"),
                    "operator": connection.get("products", [""])[0],
                    "price": connection.get("price")
                })
            
            return pd.DataFrame(buses) if buses else "No buses found"
            
        except Exception as e:
            return f"Error processing buses: {str(e)}"

    def search_trains(self, origin: str, destination: str, date: str) -> Union[pd.DataFrame, str]:
        """
        Search for train routes between two locations on a specific date
        
        Args:
            origin: Departure location
            destination: Arrival location
            date: Travel date (YYYY-MM-DD format)
            
        Returns:
            DataFrame with train options or error message
        """
        try:
            # Validate date format
            departure_date = parser.parse(date).date()
            if departure_date < datetime.now().date():
                return "Error: Date must be in the future"
                
            params = {
                "from": origin,
                "to": destination,
                "date": date,
                "transport_types": "train",
                "limit": 10
            }
            
            result = self._make_request("connections", params)
            if isinstance(result, str):
                return result
                
            trains = []
            for connection in result.get("connections", []):
                trains.append({
                    "departure": connection.get("from", {}).get("departure"),
                    "arrival": connection.get("to", {}).get("arrival"),
                    "duration": connection.get("duration"),
                    "train_type": connection.get("products", [""])[0],
                    "price": "Varies by class"  # Actual API might provide this
                })
            
            return pd.DataFrame(trains) if trains else "No trains found"
            
        except Exception as e:
            return f"Error processing trains: {str(e)}"

    def search_cabs(self, origin: str, destination: str, date: Optional[str] = None) -> Union[pd.DataFrame, str]:
        """
        Search for cab options between two locations
        
        Args:
            origin: Pickup location
            destination: Dropoff location
            date: Optional date/time (YYYY-MM-DD or YYYY-MM-DDTHH:MM format)
            
        Returns:
            DataFrame with cab options or error message
        """
        try:
            params = {
                "pickup": origin,
                "dropoff": destination,
                "time": date or datetime.now().isoformat()
            }
            
            # Using mock data since open data APIs typically don't have cab info
            cabs = [
                {
                    "provider": "City Cabs",
                    "vehicle_type": "Standard",
                    "estimated_price": "₹500-600",
                    "eta": "5-10 mins",
                    "contact": "+91 1234567890"
                },
                {
                    "provider": "Premium Taxis",
                    "vehicle_type": "SUV",
                    "estimated_price": "₹800-1000",
                    "eta": "10-15 mins",
                    "contact": "+91 9876543210"
                }
            ]
            
            return pd.DataFrame(cabs)
            
        except Exception as e:
            return f"Error processing cabs: {str(e)}"

    def book_transport(
        self,
        transport_type: str,
        option_id: str,
        passenger_details: Dict,
        payment_details: Optional[Dict] = None
    ) -> Dict:
        """
        Book a transport option
        
        Args:
            transport_type: Type of transport (flight/bus/train/cab)
            option_id: ID of the selected option
            passenger_details: Dictionary with passenger info
            payment_details: Optional payment information
            
        Returns:
            Dictionary with booking confirmation or error
        """
        try:
            # Validate inputs
            if transport_type.lower() not in ["flight", "bus", "train", "cab"]:
                return {"status": "error", "message": "Invalid transport type"}
                
            if not passenger_details.get("name") or not passenger_details.get("contact"):
                return {"status": "error", "message": "Missing required passenger details"}
                
            # Mock booking confirmation
            booking_id = f"{transport_type[:3]}-{option_id[:4]}-{datetime.now().strftime('%Y%m%d')}"
            
            return {
                "status": "success",
                "booking_id": booking_id,
                "details": {
                    "transport_type": transport_type,
                    "passenger": passenger_details,
                    "booking_time": datetime.now().isoformat(),
                    "status": "confirmed"
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Booking failed: {str(e)}"}

    def _parse_date(self, date_str: str) -> Union[date, str]:
        """Helper method to parse and validate dates"""
        try:
            parsed_date = parser.parse(date_str).date()
            if parsed_date < datetime.now().date():
                return "Error: Date must be in the future"
            return parsed_date
        except ValueError:
            return "Error: Invalid date format. Please use YYYY-MM-DD"

    def cancel_booking(self, booking_id: str, reason: Optional[str] = None) -> Dict:
        """
        Cancel a transport booking
        
        Args:
            booking_id: ID of the booking to cancel
            reason: Optional reason for cancellation
            
        Returns:
            Dictionary with cancellation status and details
        """
        try:
            # Validate booking ID format
            if not re.match(r'^(flight|bus|train|cab)-\w{4}-\d{8}$', booking_id):
                return {
                    "status": "error",
                    "message": "Invalid booking ID format"
                }

            # Prepare cancellation payload
            payload = {
                "booking_id": booking_id,
                "cancellation_time": datetime.now().isoformat()
            }
            if reason:
                payload["reason"] = reason

            # Make cancellation request
            result = self._make_request(
                endpoint=f"bookings/{booking_id}/cancel",
                params=payload,
                method="POST"
            )

            if isinstance(result, str):
                return {
                    "status": "error",
                    "message": result
                }

            # Check if cancellation was successful
            if result.get("status") == "cancelled":
                return {
                    "status": "success",
                    "message": "Booking cancelled successfully",
                    "details": {
                        "booking_id": booking_id,
                        "cancellation_time": datetime.now().isoformat(),
                        "refund_status": result.get("refund_status", "pending"),
                        "refund_amount": result.get("refund_amount")
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to cancel booking",
                    "details": result
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Cancellation failed: {str(e)}"
            }

    def get_booking_status(self, booking_id: str) -> Dict:
        """
        Get the current status of a booking
        
        Args:
            booking_id: ID of the booking to check
            
        Returns:
            Dictionary with booking status and details
        """
        try:
            result = self._make_request(
                endpoint=f"bookings/{booking_id}",
                params={}
            )

            if isinstance(result, str):
                return {
                    "status": "error",
                    "message": result
                }

            return {
                "status": "success",
                "booking_id": booking_id,
                "details": {
                    "status": result.get("status"),
                    "transport_type": result.get("transport_type"),
                    "passenger": result.get("passenger"),
                    "booking_time": result.get("booking_time"),
                    "journey_details": result.get("journey_details")
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get booking status: {str(e)}"
            }