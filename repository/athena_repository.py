import time
import boto3
import os

def ejecutar_en_athena(query):
    athena = boto3.client(
        "athena",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")
    )

    try:
        response = athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': 'farmacia_ds'},
            ResultConfiguration={'OutputLocation': os.getenv("ATHENA_OUTPUT_LOCATION")}
        )
        execution_id = response['QueryExecutionId']
        print(f"🚀 Ejecutando consulta en Athena, ID: {execution_id}")

        # Espera a que termine la ejecución
        status = 'RUNNING'
        while status in ['RUNNING', 'QUEUED']:
            time.sleep(1)
            result = athena.get_query_execution(QueryExecutionId=execution_id)
            status = result['QueryExecution']['Status']['State']

        if status == 'FAILED':
            reason = result['QueryExecution']['Status']['StateChangeReason']
            print(f"❌ Athena ERROR: {reason}")
            return {"error": f"La consulta falló: {reason}"}

        # Si fue exitosa
        data = athena.get_query_results(QueryExecutionId=execution_id)
        print(f"✅ Consulta completada con {len(data['ResultSet']['Rows'])} filas")
        return parsear_resultados(data)

    except Exception as e:
        print(f"⚠️ Excepción: {e}")
        return {"error": str(e)}


def parsear_resultados(data):
    rows = data['ResultSet']['Rows']
    headers = [col['VarCharValue'] for col in rows[0]['Data']]
    registros = []
    for row in rows[1:]:
        valores = [col.get('VarCharValue', None) for col in row['Data']]
        registros.append(dict(zip(headers, valores)))
    return registros
