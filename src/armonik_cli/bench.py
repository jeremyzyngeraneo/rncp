from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from armonik_cli.models import Campaign, Workload

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/db"

engine = create_engine(DATABASE_URL)


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

def edit_campaign(id, field, update_value ):
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


    
