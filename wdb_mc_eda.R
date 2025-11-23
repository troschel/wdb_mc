library(tidyverse)
library(lubridate)
library(ggplot2)
library(readxl)

# Read dataset with job ads
jobs <- read.csv("datasets/jobscout24_all_jobs.csv")

# Correct publishing date and time of job ads
jobs$publishing_date_corr <- sub("(\\+\\d\\d:\\d\\d):\\d\\d$", "\\1", jobs$publishing_date)
jobs$publishing_date_ymd <- ymd_hms(jobs$publishing_date_corr)
jobs$publishing_date_1 <- date(jobs$publishing_date_corr)
jobs$publishing_time <- as.POSIXct(jobs$publishing_date_ymd, format = "%H:%M:%S")

# Add cantons to dataset (merged by municipality name)
gemeinde <- read_xlsx("datasets/gemeindestand.xlsx")

# Merge two datasets
jobs <- jobs %>%
  mutate(location = tolower(location)) %>%
  left_join(
    gemeinde %>% mutate(location = tolower(Gemeindename)),
    by = "location"
  )


# Drop columns which are not needed for analysis
jobs <- jobs %>% select(title, company, quota, location, url, job_id, publishing_date_1, publishing_time, Kanton)

# Rename columns for unity in dataset
jobs <- jobs %>% rename(publishing_date=publishing_date_1) %>% rename(canton=Kanton)

# Quotas are saved as characters, sometimes with upper and lowwer quota in same character. 
# Divide quotas and save them as upper and lower quota
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

# Boxpolt displaying publishing date nationwide
ggplot(data=jobs, aes(publishing_date))+geom_boxplot()+theme_minimal()+
  labs(title="Distribution of publishing dates for job ads",
       x="Publishing date")+coord_flip()+theme(axis.text.x = element_blank())

# Boxplot displaying publishing date by cantons
jobs %>% filter(!is.na(canton)) %>% ggplot(aes(canton, publishing_date)) + geom_boxplot() + theme_minimal()+
  labs(title="Publishing dates by cantons",
       x="Canton",
       y="Publishing date")

# Lower and higher quota plot
ggplot() +
  geom_density(data = jobs, aes(x = quota_low, colour = "Low quota")) +
  geom_density(data = jobs, aes(x = quota_high, colour = "High quota")) +
  scale_colour_manual(values = c("Low quota" = "blue",
                                 "High quota" = "red")) +
  theme_minimal() +
  labs(title = "Lower and higher quotas in job ads",
       x = "Quota",
       y = "Density",
       colour = "Type")

