from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.providers.docker.operators.docker import DockerOperator

from airflow.models import Variable

CHAPI__MSP_TO_DASHBOARDS = {
    "BROKER_MSP": [
        "MatomoActionsAnalisys",
        "MatomoClientAnalytics",
        "MatomoBasicIndicators",
    ],
    "INSURANCE_MSP": [
        "SLDashboardV3",
        "ClaimsAnalytics",
        "EmployeesAnalytics",
        "ArrangementModuleVisits",
        "GeneralStatistics",
        "DashboardFromHomePageInsurance",
        "MatomoBasicIndicatorsInsurance",
        "EmployeeStatistics",
        "ArrangementDashboard",
    ],
    "TRANSPORT_MSP": ["EveryWeekDashboard"],
}

CMD_PARAMS = [
    "locust -f /app/run/chapi_main.py",
    # "--loglevel ERROR",
    # "--logfile log.log",
    "--headless -u 10 -r 1 -t 10m",
    "--env dev",
    "--entity_name chapi",
    f"--yp_s3_access_code {Variable.get('YP_AWS_ACCESS_CODE')}",
    f"--yp_s3_secret_code {Variable.get('YP_AWS_SECRET_CODE')}"
]
BASE_CMD = " ".join(CMD_PARAMS)
 
with DAG(
    dag_id="bi-chapi_loading_tests-dev",
    start_date=days_ago(1),
    schedule=None
) as dag:
    for msp_serv in CHAPI__MSP_TO_DASHBOARDS:
        with TaskGroup(
            group_id=f"tg_{msp_serv.lower()}",
        ) as tg:
            for dash_name in CHAPI__MSP_TO_DASHBOARDS[msp_serv]:
                start_docker_run = DockerOperator(
                    task_id=f"start_docker_run__{msp_serv.lower()}_{dash_name}",
                    container_name=f"{msp_serv.lower()}_{dash_name}",
                    image="bi-loading-tests:latest",
                    api_version="1.30",
                    auto_remove=True,
                    mount_tmp_dir=False,
                    docker_url="tcp://docker-socket-proxy:2375",
                    command=f"{BASE_CMD} --csv={msp_serv}_{dash_name} --msp {msp_serv} --dash_name {dash_name}",
                    network_mode="host",
                    skip_on_exit_code=1
                )
