# SERVER manipula los datos que pinta UI
shinyServer(function(input, output,session) {
  tabPanel(value = "staticmapa",
    # dibujar mapa inicial
    output$mapa <- renderLeaflet({leaflet() %>% addTiles() %>% setView(lng = -4.62473, lat = 36.53998, zoom = 12)}),
    # filtrado de expedientes
    filtroexpedientes <- reactive({
      filtroexpedientes <-  expedientes[expedientes$Fecha >= input$fechas[1] & expedientes$Fecha <= input$fechas[2],]
      filtroexpedientes <- filtroexpedientes %>% filter(filtroexpedientes$T1 %in% input$tipoincidencia)
    }),
    # paleta de colores
    pal <- c("red","blue","darkblue","green","orange","gray","lightgreen","pink","brown","black"),
    # uso de proxy de mapa
    observe({
      leafletProxy(mapId = "mapa", data = filtroexpedientes() ) %>% clearMarkers() %>%
      #  addHeatmap(lng=filtroexpedientes()$X,lat=filtroexpedientes()$Y, radius=15, blur=10)
        addAwesomeMarkers(data=filtroexpedientes(), lng = ~X, lat = ~Y,
              popup = paste0(
                  "<b> INCIDENCIA: </b>",
                  "<br>Nivel 1: ", filtroexpedientes()$T1,
                  "<br>Nivel 2: ", filtroexpedientes()$T2,
                  "<br>Nivel 3: ", filtroexpedientes()$T3,
                  "<br>",
                  "<br>FECHA: ", filtroexpedientes()$Fecha
              ),
              icon = awesomeIcons(library = "ion", icon = "ion-arrow-down-b",
                markerColor = ifelse(test = filtroexpedientes()$T1 == incidencias[1], yes = pal[1],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[2], yes = pal[2],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[3], yes = pal[3],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[4], yes = pal[4],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[5], yes = pal[5],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[6], yes = pal[6],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[7], yes = pal[7],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[8], yes = pal[8],
                  no = ifelse(test = filtroexpedientes()$T1 == incidencias[9], yes = pal[9],
                  no = pal[10]
                  )))))))))
              )
        )
      output$Nincidencias <- renderInfoBox({
        valueBox(nrow(filtroexpedientes()), "Seleccionadas",  icon = icon("list"),color = "aqua")
  ###      valueBox("Predicción","Seleccionadas",  icon = icon("list"),color = "aqua")
      })
    })
 )
 tabPanel(value = "grafs",
      output$mapablanco <- renderLeaflet(leaflet())
      #output$histogramas <- renderPlot(),
      #output$temporal <- renderPlot()
 )
 tabPanel(value = "correla",
  # dibujar gráfica
    output$heatall <- renderPlot({
     heatmap(pmi, col=bluered(100), labRow = levels(expedientes$T1), labCol=levels(expedientes$T1),margins =c(12,9))
        #        dendrogram = "none",cellnote = pmi)
    })
 )
})

