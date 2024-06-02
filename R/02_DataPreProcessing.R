### ASSET ALLOCATION - DATA PRE PROCESSING MODULE (functions)
library(zoo)

sp_preProcessing <- function(sp_xls){

  output <- sp_xls[(which(sp_xls[,1] == "Effective date") + 1):(nrow(sp_xls) - 4),] %>% 
    setNames(c("DATE", "PRICE")) %>% 
    mutate(DATE = DATE %>% as.numeric() %>% as.Date(origin = "1899-12-30"))
  
  return(output)
  
}

yahoo_preProcessing <- function(yahoo_csv){
  
  col_names <- colnames(yahoo_csv)
  open_col <- col_names[grepl(pattern = "Open", x = col_names)]
  high_col <- col_names[grepl(pattern = "High", x = col_names)]
  low_col <- col_names[grepl(pattern = "Low", x = col_names)]
  close_col <- col_names[grepl(pattern = "Close", x = col_names)]
  volume_col <- col_names[grepl(pattern = "Volume", x = col_names)]
  adjusted_col <- col_names[grepl(pattern = "Adjusted", x = col_names)]
  
  output <- yahoo_csv %>% 
    rename(DATE = index) %>% 
    rename(OPEN := sym(open_col)) %>% 
    rename(HIGH := sym(high_col)) %>% 
    rename(LOW := sym(low_col)) %>% 
    rename(CLOSE := sym(close_col)) %>% 
    rename(VOLUME := sym(volume_col)) %>% 
    rename(PRICE := sym(adjusted_col)) %>% 
    select(DATE, PRICE) # same format as sp sourcing
  
  return(output)
}

preProcessing <- function(loadedData){
  
  loadedData[["sp"]] <- loadedData[["sp"]] %>% lapply(FUN = function(x) sp_preProcessing(x))
  loadedData[["yahoo"]] <- loadedData[["yahoo"]] %>% lapply(FUN = function(x) yahoo_preProcessing(x))
  
  output <- c(loadedData[["sp"]], loadedData[["yahoo"]])
  return(output)
  
}

fxProcessing <- function(pre_processed_fx_data){
  
  daily_fill <- function(yahoo_fx_csv){
    start_date = yahoo_fx_csv %>% pull(DATE) %>% min()
    end_date = yahoo_fx_csv %>% pull(DATE) %>% max()
    
    dates <- seq(from = start_date, to = end_date, by = "day")
    
    output <- data.frame(DATE = dates)
    output <- left_join(output, yahoo_fx_csv, by = "DATE")
    return(output)
  }
  
  
  
  fxSeriesInterpolation <- function(yahoo_fx_csv){
    if(!all(c("DATE", "PRICE") %in% names(yahoo_fx_csv))) {
      stop("Dataframe must contain 'DATE' and 'PRICE' columns.")
    }
    
    yahoo_fx_csv$DATE <- as.Date(yahoo_fx_csv$DATE)
    yahoo_fx_csv <- yahoo_fx_csv %>% arrange(DATE)
    
    price_zoo <- zoo(yahoo_fx_csv$PRICE, order.by = yahoo_fx_csv$DATE)
    interpolated_price_zoo <- na.approx(price_zoo, rule = 2)
    
    yahoo_fx_csv$PRICE <- coredata(interpolated_price_zoo)
    return(yahoo_fx_csv)
  }
  
  output <- pre_processed_fx_data %>% lapply(FUN = function(x) x %>% daily_fill() %>% fxSeriesInterpolation())
  return(output)
  
}

