#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(datasets)

data2010 <- read.csv('BP Apprehensions 2010.csv')
data2017 <- read.csv('PB Apprehensions 2017.csv')


# Define UI for application that draws a histogram
ui <- fluidPage(
  
  titlePanel("BP Apprehensions in 2010 and 2017"),
  
  sidebarLayout(
    sidebarPanel(
      
      selectInput('comp', 'Choose comparison', 
                  choices = c('Big Bend' = '1', 'Del Rio' = '2', 'El Centro' = '3', 'El Paso' = '4', 'Laredo' = '5', 'Rio Grande Valley' = '6', 'San Diego' = '7', 'Tuscon' = '8', 'Yuma' = '9')
                  )
    ),
  
    mainPanel(
      
      plotOutput("appPlot")
    )
  )
)

  
  
# Define server logic required to draw a histogram
server <- function(input, output) {
  
  selectedData <- reactive({
    colu = as.numeric(input$comp)
    colu
    d1 = as.data.frame(data2010[,c(colu)])
    colnames(d1) <- c("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    d2 = as.data.frame(data2017[,c(colu)])
    colnames(d2) <- c("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    
    mydata <- rbind(d1, d2)
    
  })

  output$appPlot <- renderPlot({
    
    
    barplot(as.matrix(data), beside = TRUE, col = c("yellow", "blue"), bty="n" )
    
    legend("topleft", c("2010","2017"), pch=15,  col=c("yellow","blue"),  bty="n")
     
   })
}

# Run the application 
shinyApp(ui = ui, server = server)

