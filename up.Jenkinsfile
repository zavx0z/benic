def remote = [:]
remote.name = "root"
remote.host = params.IP
remote.allowAnyHosts = true
remote.user = "root"

pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '4', artifactNumToKeepStr: '4'))
        disableConcurrentBuilds(abortPrevious: true)
    }
    parameters {
        string( name: 'IP', defaultValue: "95.163.235.179", description: 'IP-адрес сервера')
        string( name: 'DOMAIN', defaultValue: "zavx0z.com")

        string( name: 'STORE_DIR', defaultValue: "/store")
        string( name: 'EMAIL', defaultValue: "metaversebdfl@gmail.com")

        string( name: 'POSTGRES_HOST', defaultValue: "db")
        string( name: 'POSTGRES_PORT', defaultValue: "5432")
        string( name: 'POSTGRES_USER', defaultValue: "zavx0zBenif")
        string( name: 'POSTGRES_DB', defaultValue: "benif")
        string( name: 'POSTGRES_PASSWORD', defaultValue: "12112022")

        string( name: 'JWT_SECRET_KEY', defaultValue: "adkngdfFDGSDFqhnlakjflorqirefOJ;SJDG")

        booleanParam(name: 'rmDB', defaultValue: false, description: 'Очистить базу данных')
        booleanParam(name: 'Refresh', defaultValue: false, description: 'Перезагрузка параметров')
    }
    environment {
        ROOT_APP_DIR='/app'
        POSTGRES_DIR="${STORE_DIR}/db"
        DRAMATIQ_DIR="${STORE_DIR}/dramatiq"

        APP_HOST='app'
        REDIS_HOST="redis"
        REDIS_PORT=6379

        REMOTE_ENV_PATH = "${ROOT_APP_DIR}/app/.env"
        LOCAL_ENV_PATH = "${WORKSPACE}/.env"
    }
    stages {
        stage('Перезагрузка параметров') {
            when { expression { return params.Refresh == true } }
            steps { echo("Ended pipeline early.") }
        }
        stage('Переменные окружения') {
            when { expression { return params.Refresh == false } }
            steps {
                sh script: "rm ${LOCAL_ENV_PATH}"
                writeFile file: LOCAL_ENV_PATH,
                text: """
POSTGRES_DIR=${env.POSTGRES_DIR}
POSTGRES_HOST=${params.POSTGRES_HOST}
POSTGRES_PORT=${params.POSTGRES_PORT}
POSTGRES_DB=${params.POSTGRES_DB}
POSTGRES_USER=${params.POSTGRES_USER}
POSTGRES_PASSWORD=${params.POSTGRES_PASSWORD}

APP_HOST=${env.APP_HOST}

DOMAIN=${params.DOMAIN}
EMAIL=${params.EMAIL}
JWT_SECRET_KEY=${params.JWT_SECRET_KEY}

DRAMATIQ_DIR=${env.DRAMATIQ_DIR}
REDIS_HOST=${env.REDIS_HOST}
REDIS_PORT=${env.REDIS_PORT}
""",
                encoding: "UTF-8"
            }
        }
        stage('Остановка') {
            when { expression { return params.Refresh == false } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script { remote.identityFile = sshKey }
                    sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml stop", failOnError: false
                    sshCommand remote: remote, command: "docker stop nginx", failOnError: false
                }
            }
        }
        stage('Удаление') {
            when { expression { return params.Refresh == false } }
            steps {
                script {
                    withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                        remote.identityFile = sshKey
                        sshCommand remote: remote, command: "rm -rf ${ROOT_APP_DIR}"
                        if (params.rmDB == true) {
                            sshCommand remote: remote, command: "rm -rf ${POSTGRES_DIR}"
                        }
                    }
                }
            }
        }
        stage('Копирование') {
            when { expression { return params.Refresh == false } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script { remote.identityFile = sshKey }
                    sh script: 'scp -i ${sshKey} -rp ${WORKSPACE} root@${IP}:${ROOT_APP_DIR}', returnStdout: true
                }
            }
        }
        stage('Сборка') {
            when { expression { return params.Refresh == false } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script { remote.identityFile = sshKey }
                    sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml build"
                }
            }
        }
        stage('Запуск') {
            when { expression { return params.Refresh == false } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script { remote.identityFile = sshKey }
                    sshCommand remote: remote, command: "docker-compose -f ${ROOT_APP_DIR}/docker-compose.yml up -d"
                    sshCommand remote: remote, command: "docker start nginx"
                }
            }
        }
        stage('Вывод лога') {
            when { expression { return params.Refresh == false } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script { remote.identityFile = sshKey }
                    sshCommand remote: remote, command: "docker logs app"
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
