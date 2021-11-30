# UI pinta los gráficos
shinyUI(dashboardPage(
  dashboardHeader(title = "POLICÍA LOCAL"),
    #title = tags$a(href="",tags$img(src='logoPOL.jpg'),"POLICIA LOCAL")),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Inicio", tabName = "instrucciones", icon=icon("home"), selected = T),
      menuItem("Visualización callejero", tabName = "staticmapa", icon=icon("map")),
      menuItem("Gráficos incidencias", tabName = "grafs", icon=icon("bar-chart")),
      menuItem("Predicción incidencias", tabName = "correla", icon=icon("th"))
    )
  ),
  dashboardBody(tabItems(
    tabItem("instrucciones"
        # box(width=12, imageOutput("logo"))
        # img(src = 'logo', align="center")
        # tags$img(src = "logoPOL.jpg", height = 400, width = 400, align='center')
    ),
    tabItem("staticmapa",
      fluidRow(
        box(width=8, leafletOutput(outputId = "mapa")),
        box(width = 4, background = "light-blue", #title = "Selección", 
          checkboxGroupInput(inputId = "tipoincidencia", 
                             label = h4("Tipo de Incidencias: "),
                             choices = incidencias, 
                             selected = "none",
                             inline = FALSE
                             )
        ),
        valueBoxOutput("Nincidencias", width = 4)
      ),
      fluidRow(
        box(width = 12, #title = h5("Intervalo de fechas"),
          sliderInput(inputId = "fechas", "", 
                      min = as.Date("2016-01-01"), 
                      max = as.Date("2018-12-31"), 
                      value = c(as.Date("2016-11-01"),as.Date("2017-03-01"))))
      )
    ),
    tabItem("grafs",
      fluidRow(
            box(width = 8, plotOutput("timegraf")),
            box(width = 4, background = "light-blue",
                checkboxGroupInput(inputId = "tipograf", label = h4("Categorías: "),
                                   choices = incidencias,
                                   selected = "none", inline = FALSE)
               )
      )
    ),
    tabItem("correla",
          fluidRow(
            box(width = 12, plotOutput("heatall"))
            # box(width = 4, background = "light-blue",
            #     checkboxGroupInput(inputId = "tipocorrela", label = h4("Categorías a correlar: "),
            #                        choices = incidencias, selected = "none", inline = FALSE))
          )
    )
  )) #close dashBody + tabItems
)) #close shinyUI + dashPage
