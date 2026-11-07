
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

BANK_ID = "foundrymind"

try:
    # Store a manufacturing incident
    client.retain(
        bank_id=BANK_ID,
        content=(
            "Incident ID F-001: A sand core had a broken edge. "
            "The team recorded the incident and investigated "
            "mould handling and core condition. The outcome "
            "requires verification before confirming a cause."
        ),
    )

    print("Incident submitted to Hindsight!")

    # Search for the incident
    input("Wait a few seconds, then press Enter to recall it...")

    result = client.recall(
        bank_id=BANK_ID,
        query="What previous manufacturing incident involved "
              "a broken edge in a sand core?",
    )

    print("\nRecalled memories:")
    for memory in result.results:
        print("-", memory.text)

except Exception as e:
    print("Error:", e)

finally:
    client.close()

