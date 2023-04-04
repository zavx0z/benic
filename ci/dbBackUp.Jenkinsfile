def remote = [:]
remote.name = "root"
remote.host = params.IP
remote.allowAnyHosts = true
remote.user = "root"

pipeline {
    agent any
    parameters {
        string(name: 'IP', defaultValue: '95.163.235.179', description: 'IP-адрес сервера')
        string(name: 'TO', defaultValue: '/media/hdd/backUp', description: 'Каталог для сохранения резервной копии')
        string(name: 'CONTAINER_NAME', defaultValue: 'db', description: 'Имя контейнера PostgreSQL')
        string(name: 'POSTGRES_USER', defaultValue: 'zavx0zBenif', description: 'Имя пользователя PostgreSQL')
        string(name: 'POSTGRES_DB', defaultValue: 'benif', description: 'Имя базы данных PostgreSQL')
        booleanParam(name: 'REFRESH', defaultValue: false, description: 'Перезагрузка параметров')
    }
    stages {
        stage('Перезагрузка параметров') {
            when { expression { return params.Refresh == true } }
            steps { echo("Ended pipeline early.") }
        }
        stage ('Бэкап') {
            when { expression { return params.Refresh == false } }
            steps {
                build job: 'postgresBackUp', wait: true, parameters: [
                    string( name: 'IP', value: IP),
                    string( name: 'TO', value: TO),
                    string( name: 'CONTAINER_NAME', value: CONTAINER_NAME),
                    string( name: 'POSTGRES_USER', value: POSTGRES_USER),
                    string( name: 'POSTGRES_DB', value: POSTGRES_DB),
                ]
            }
        }
    }
    post {
        always {
            emailext (
                subject: "${currentBuild.fullDisplayName} - ${currentBuild.currentResult}",
                body: """\
                    <p>Завершено: ${currentBuild.fullDisplayName} - ${currentBuild.currentResult}</p>
                """,
                to: "recipient@example.com",
                attachLog: true,
            )
        }
    }
}
