from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.docker.operators.docker import DockerOperator

REAPI__MSP_SERVICES = ["BROKER_MSP", "INSURANCE_MSP", "TRANSPORT_MSP"]

 
with DAG(
    dag_id="bi-reapi_loading_tests-dev",
    start_date=days_ago(1),
    schedule=None
) as dag:
    
    for msp_serv in REAPI__MSP_SERVICES:
        start_docker_run = DockerOperator(
            task_id=f"start_docker_run__{msp_serv.lower()}",
            container_name=f"{msp_serv.lower()}",
            image="bi-loading-tests:latest",
            api_version="1.30",
            auto_remove=True,
            mount_tmp_dir=False,
            docker_url="tcp://docker-socket-proxy:2375",
            command=f"python -m locust -f /app/run/reapi_main.py --csv={msp_serv} --headless -u 10 -r 1 -t 10m --msp {msp_serv}",
            network_mode="host"
        )
