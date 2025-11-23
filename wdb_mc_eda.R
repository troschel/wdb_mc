library(tidyverse)
library(lubridate)
library(ggplot2)
library(readxl)

jobs <- read.csv("~datasets/jobscout24_all_jobs.csv")


jobs$publishing_date_corr <- sub("(\\+\\d\\d:\\d\\d):\\d\\d$", "\\1", jobs$publishing_date)
jobs$publishing_date_ymd <- ymd_hms(jobs$publishing_date_corr)
jobs$publishing_date_1 <- date(jobs$publishing_date_corr)
#jobs$publishing_time <- format(jobs$publishing_date_ymd, "%H:%M:%S")
jobs$publishing_time <- as.POSIXct(jobs$publishing_date_ymd, format = "%H:%M:%S")
gemeinde <- read_xlsx("/Users/pascaltrosch/Documents/wdb/gemeindestand.xlsx")

jobs <- jobs %>%
  mutate(location = tolower(location)) %>%
  left_join(
    gemeinde %>% mutate(location = tolower(Gemeindename)),
    by = "location"
  )



jobs <- jobs %>% select(title, company, quota, location, url, job_id, publishing_date_1, publishing_time, Kanton)

jobs <- jobs %>% rename(publishing_date=publishing_date_1) %>% rename(canton=Kanton)
jobs <- jobs %>%
  mutate(
    quota_clean = str_replace_all(quota, "[ %]", ""),
    quota_clean = str_replace_all(quota_clean, "–", "-"),
    
    # split into low and high
    quota_low  = as.numeric(str_extract(quota_clean, "^[0-9]+")),
    quota_high = as.numeric(str_extract(quota_clean, "(?<=-)[0-9]+")),
    
    # if high is missing, set equal to low
    quota_high = ifelse(is.na(quota_high), quota_low, quota_high)
  )


jobs %>% filter(!is.na(canton)) %>% ggplot(aes(canton, publishing_date)) + geom_boxplot() + theme_minimal() + 
ggplot() +
  geom_density(data = jobs, aes(x = quota_low), colour = "blue") +
  geom_density(data = jobs, aes(x = quota_high), colour = "red")
