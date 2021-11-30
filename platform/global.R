library(shiny)
library(shinydashboard)

# cargar los paquetes necesarios
packages <- c("data.table","dplyr","tidyverse",
              "lubridate","kdensity","gplots",
              "leaflet","ggplot2","ECharts2Shiny",
              "heatmaply","shinyHeatmaply")
installed_packages <- packages %in% rownames( installed.packages() )
if (any(installed_packages == FALSE)) {
  install.packages(packages[!installed_packages], repos = "http://cran.us.r-project.org")
}
invisible(lapply(packages, library, character.only = TRUE))

# cargar funciones y expedientes
source('../rstudio/analysis.R')
expedientes<-read.table("../all-data.tsv", sep="\t",header=TRUE)
expedientes$Fecha <- ymd_hms(expedientes$Fecha)

expedientes <- expedientes[1:500,]

incidencias <- c("1 TRÁFICO","2 SEGURIDAD CIUDADANA",
                 "3 ADMINISTRATIVA","4 EXTINCIÓN INCENDIOS",
                 "5 HUMANITARIOS", "6 ATENCIÓN LLAMADAS", 
                 "7 REQUERIMIENTOS", "8 SOLICITUD DE SERVICIOS", 
                 "9 DATOS","0 SIN ASIGNAR")

# Relación de incidencias
all.interactions <- table.related.events(expedientes,0.200, dminutes(30))
pairs<- buil.pairs(all.interactions)
m<-build.matrix(expedientes, pairs)
pmi <- positive.mi.matrix(m)

