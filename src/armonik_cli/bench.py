import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from armonik_cli.models import Campaign, Workload
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not defined in .env")

engine = create_engine(database_url)


def print_workloads():
    session = Session(engine)
    stmt = select(Workload)
    for workload in session.scalars(stmt):
        print(workload.name)


def list_campaigns():
    session = Session(engine)
    stmt = select(Campaign)
    for campaign in session.scalars(stmt):
        print(f"campaign_id: {campaign.campaign_id}, name: {campaign.name}")


def get_campaign(id):
    session = Session(engine)
    stmt = select(Campaign).where(Campaign.campaign_id.in_(id))
    for campaign in session.scalars(stmt):
        print(campaign)


def edit_campaign(id, field, update_value):
    session = Session(engine)
    stmt = select(Campaign).where(Campaign.campaign_id == id)
    campaign_field = session.scalar(stmt)
    setattr(campaign_field, field, update_value)
    session.commit()


def delete_campaign(id):
    session = Session(engine)
    stmt = select(Campaign).where(Campaign.campaign_id == id)
    campaign_to_delete = session.scalar(stmt)
    session.delete(campaign_to_delete)
    session.commit()


def create_campaign(json_path):
    with open(json_path, "r") as file:
        campaign_data = json.load(file)

        campaign_id = campaign_data.get("campaign_id")
        name = campaign_data.get("name")
        description = campaign_data.get("description")
        author = campaign_data.get("author")
        status = campaign_data.get("status")
        created_at = datetime.fromtimestamp(campaign_data.get("created_at"))
        updated_at = datetime.fromtimestamp(campaign_data.get("updated_at"))

    with Session(engine) as session:
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            description=description,
            author=author,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )
        session.add(campaign)
        session.commit()
        print("Campaign created successfully")
