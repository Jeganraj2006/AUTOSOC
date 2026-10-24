import argparse
import sys
import logging
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("provision-topics")

REQUIRED_TOPICS = {
    "security.events.raw": {
        "num_partitions": 3,
        "replication_factor": 1, # Development default
        "config": {
            "retention.ms": "604800000", # 7 days
            "cleanup.policy": "delete"
        }
    },
    "security.events.failed": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",
            "cleanup.policy": "delete"
        }
    },
    "security.events.normalized": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",
            "cleanup.policy": "delete"
        }
    },
    "security.events.enriched": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "604800000",
            "cleanup.policy": "delete"
        }
    },
    "security.alerts": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "2592000000", # 30 days
            "cleanup.policy": "delete"
        }
    },
    "security.incidents": {
        "num_partitions": 3,
        "replication_factor": 1,
        "config": {
            "retention.ms": "2592000000", # 30 days
            "cleanup.policy": "delete"
        }
    }
}

def provision_topics(bootstrap_servers: str):
    logger.info(f"Connecting to Redpanda at {bootstrap_servers}")
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id="topic_provisioner"
        )
    except KafkaError as e:
        logger.error(f"Failed to connect to Redpanda: {e}")
        sys.exit(1)
        
    existing_topics = admin_client.list_topics()
    new_topics = []
    
    for topic_name, config in REQUIRED_TOPICS.items():
        if topic_name in existing_topics:
            logger.info(f"Topic '{topic_name}' already exists. Skipping creation.")
            # Note: updating config for existing topics is possible but omitted for MVP safety
        else:
            logger.info(f"Preparing to create topic '{topic_name}'")
            new_topics.append(
                NewTopic(
                    name=topic_name,
                    num_partitions=config["num_partitions"],
                    replication_factor=config["replication_factor"],
                    topic_configs=config["config"]
                )
            )
            
    if new_topics:
        try:
            admin_client.create_topics(new_topics=new_topics, validate_only=False)
            for t in new_topics:
                logger.info(f"Successfully created topic: {t.name}")
        except TopicAlreadyExistsError as e:
            logger.warning(f"Topic already exists during creation (race condition): {e}")
        except Exception as e:
            logger.error(f"Failed to create topics: {e}")
            admin_client.close()
            sys.exit(1)
    else:
        logger.info("No new topics required.")
        
    admin_client.close()
    logger.info("Topic provisioning complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision Redpanda/Kafka topics for AutoSOC")
    parser.add_argument("--bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    args = parser.parse_args()
    
    provision_topics(args.bootstrap_servers)
