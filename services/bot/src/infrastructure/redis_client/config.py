from redis.asyncio.cluster import RedisCluster, ClusterNode
from pydantic import Field
from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):
    redis_nodes: list[str] = Field()
    redis_password: str = Field()
    redis_user: str = Field()


def setup_client(cfg: RedisConfig) -> RedisCluster:
    cluster_nodes: list[ClusterNode] = []
    for node in cfg.redis_nodes:
        host, port = node.split(":")
        cluster_node = ClusterNode(
            host=host,
            port=port,
        )
        cluster_nodes.append(cluster_node)
    return RedisCluster(
        startup_nodes=cluster_nodes,
        username=cfg.redis_user,
        password=cfg.redis_password,
    )
