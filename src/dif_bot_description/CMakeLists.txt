cmake_minimum_required(VERSION 3.8)
project(dif_bot_description)

find_package(ament_cmake REQUIRED)

# Instala urdf, launch, rviz, config y worlds para que sean visibles
# desde el paquete instalado (share/dif_bot_description/...)
install(
  DIRECTORY urdf launch rviz config worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
