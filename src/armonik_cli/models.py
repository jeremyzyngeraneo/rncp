from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    __tablename__ = "campaign"
    campaign_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    author = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return (
            f"Campaign ID: {self.campaign_id}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Author: {self.author}\n"
            f"Status: {self.status}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}\n"
        )


class Environment(Base):
    __tablename__ = "environment"
    infrastructure_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    environment = Column(String)
    repo = Column(String)
    ref = Column(String)
    config = Column(JSON)


class Workload(Base):
    __tablename__ = "workload"
    workload_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    image = Column(String)
    tag = Column(String)
    config = Column(JSON)


class Experiment(Base):
    __tablename__ = "experiment"
    experiment_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    workload_id = Column(Integer, ForeignKey("workload.workload_id"))
    environment_id = Column(Integer, ForeignKey("environment.infrastructure_id"))


class ExperimentRun(Base):
    __tablename__ = "experiment_run"
    experiment_run_id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    duration = Column(Integer)
    db_dump = Column(String)
    logs_dump = Column(String)
    metrics_dump = Column(String)
    analysis_outputs = Column(JSON)
    outputs = Column(JSON)
    metadata_ = Column("metadata", JSON)
    experiment_id = Column(Integer, ForeignKey("experiment.experiment_id"))


class CampaignExperiment(Base):
    __tablename__ = "campaign_experiment"
    experiment_id = Column(
        Integer, ForeignKey("experiment.experiment_id"), primary_key=True
    )
    campaign_id = Column(Integer, ForeignKey("campaign.campaign_id"), primary_key=True)
