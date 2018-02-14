
  
  yearA <- as.data.frame(matrix(c(2, 3, 4, 8),nrow = 1) )
  
  colnames(yearA) <- c("Sector A", "Sector B", "Sector C", "Sector D")

  yearB<- as.data.frame(matrix(c(6, 4, 2, 4),nrow = 1) )
  
  colnames(yearB) <- c("Sector A", "Sector B", "Sector C", "Sector D")

  yearAB <- rbind(yearA, yearB)
  
  row.names(yearAB) <- c("yearA", "yearB")
  
  
  #see https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/barplot.html
  # https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/par.html

  
  show(yearAB)
  
  barplot(as.matrix(yearAB), beside = TRUE, col = c("red", "blue"), bty="n" )
  
  legend("topleft", c("yearA","yearB"), pch=15,  col=c("red","blue"),  bty="n")
  
  