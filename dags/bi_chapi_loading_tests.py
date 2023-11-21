from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.docker.operators.docker import DockerOperator

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
 
with DAG(
    dag_id="bi-chapi_loading_tests-dev",
    start_date=days_ago(1),
    schedule=None
) as dag:
    
    for msp_serv, dash_names in CHAPI__MSP_TO_DASHBOARDS.items():
        for dash_name in dash_names:
            start_docker_run = DockerOperator(
                task_id=f"start_docker_run__{msp_serv.lower()}_{dash_name}",
                container_name=f"{msp_serv.lower()}_{dash_name}",
                image="bi-loading-tests:latest",
                api_version="1.30",
                auto_remove=True,
                mount_tmp_dir=False,
                docker_url="tcp://docker-socket-proxy:2375",
                command=f"python -m locust -f /app/run/chapi_main.py --csv={msp_serv}_{dash_name} --headless -u 10 -r 1 -t 10m --msp {msp_serv} --dash_name {dash_name}",
                network_mode="host"
            )
