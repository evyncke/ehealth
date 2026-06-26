#!/usr/bin/env python3

#Copyright 2026 Eric Vyncke evyncke@cisco.com

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import requests
import pandas as pd
import time

def fetch_ietf_registrations():
    base_url = "https://datatracker.ietf.org/api/v1/meeting/registration/"
    all_registrations = []
    
    # Iterate through meeting numbers 120 to 125
    for meeting_num in range(120, 126):
        print(f"Fetching data for meeting {meeting_num}...")
        offset = 0
        limit = 20
        
        while True:
            params = {
                'meeting__number': meeting_num,
                'limit': limit,
                'offset': offset,
                'format': 'json',
                'tickets__attendance_type': 'onsite'
            }
            
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                objects = data.get('objects', [])
                if not objects:
                    break
                
                # Add meeting_number to each record
                for obj in objects:
                    obj['meeting_number'] = meeting_num
                
                all_registrations.extend(objects)
                
                # Check if we have reached the end of the records
                if len(objects) < limit:
                    break
                
                offset += limit
                # Respectful delay to avoid hitting rate limits
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for meeting {meeting_num}: {e}")
                break
    
    # Create DataFrame and export to CSV
    if all_registrations:
        df = pd.DataFrame(all_registrations)
        df.to_csv("ietf_registrations.csv", index=False)
        print("Successfully saved data with meeting numbers to ietf_registrations.csv")
    else:
        print("No data found to export.")

if __name__ == "__main__":
    fetch_ietf_registrations()
