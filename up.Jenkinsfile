pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr: '4', artifactNumToKeepStr: '4'))
        disableConcurrentBuilds(abortPrevious: true)
    }
    parameters {
        string( name: 'host', defaultValue: "95.163.235.179", description: 'Адрес сервера')
        booleanParam(name: 'clear', defaultValue: false, description: 'Перезаписать')
    }
    environment {
        ROOT_APP_DIR='/app'
    }
    stages {
        stage('Удалить проект') {
            when { expression { return params.clear } }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script {
                        def result = sh (
                            script: 'ssh -i ${sshKey} root@${host} -C rm -rf ${ROOT_APP_DIR}',
                            returnStdout: true
                        )
                        echo result
                    }
                }
            }
        }
        stage('Копирование проекта') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script {
                        def result = sh (
                            script: 'scp -i ${sshKey} -rp ${WORKSPACE} root@${host}:${ROOT_APP_DIR}',
                            returnStdout: true
                        )
                        echo result
                    }
                }
            }
        }
        stage('Сборка и запуск контейнеров') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'repozitarium', keyFileVariable: 'sshKey')]) {
                    script {
                        def resultDown = sh (
                            script: "ssh -i ${sshKey} root@${host} -C cd ${ROOT_APP_DIR} && docker-compose down",
                            returnStdout: true
                        )
                        echo resultDown

                        def resultBuild = sh (
                            script: "ssh -i ${sshKey} root@${host} -C cd ${ROOT_APP_DIR} && docker-compose build",
                            returnStdout: true
                        )
                        echo resultBuild

                        def resultUp = sh (
                            script: "ssh -i ${sshKey} root@${host} -C cd ${ROOT_APP_DIR} && docker-compose up -d",
                            returnStdout: true
                        )
                        echo resultUp
                    }
                }
            }
        }
    }
}
