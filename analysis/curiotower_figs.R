library(tidyverse)
library(lme4)
library(lmerTest)

theme_set(theme_classic())
theme_update(# axis labels
  axis.title = element_text(size = 28),
  # tick labels
  axis.text = element_text(size = 24),
  # title 
  title = element_text(size = 24),
  legend.position = 'FALSE', 
  text = element_text(size=16), 
  element_line(size=1), 
  element_rect(size=2, color="#00000"))

primary_color = '#22AAAA'
secondary_color = '#252b31'
tertiary_color = '#c7cedf'

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
dat = read_csv('curiotower_raw_data_run_0.csv')
glimpse(dat)
dat = dat %>% select('button_pressed',
                     'num_blocks',
                     'stability',
                     'viewpoint',
                     'towerID',
                     'prolificID', 
                     'condition')
dat$stability_factor = factor(dat$stability, levels = c("low", "med", "high"))
dat$button_pressed = dat$button_pressed+1 #fix 0 base
glimpse(dat)
df = dat %>% 
  group_by(towerID,condition, stability_factor, num_blocks) %>% 
  summarise(avg_rating = mean(button_pressed))
df = spread(df,condition,avg_rating )
df

ggplot()+ 
  geom_point(data = df, aes(x = stable, y = interesting,
                              color = stability_factor,
                              shape = factor(num_blocks)), 
             size = 6, 
             position='dodge') +
  scale_color_discrete(name = "jitter", labels = c("low", "med", "high"))+
  scale_shape_discrete(name = "num block", labels = c("2", "4", "8"))+
  scale_color_manual(name = "jitter",values=c(new_color,
                                              secondary_color,
                                              tertiary_color))+
  theme(legend.position = "right",
        legend.title = element_text(size = 20),
        legend.text = element_text(size = 14))



#-----------------------------------
#COOL TOWER FIGS
df_rating = read_csv('curiotower_cooltower_raw_data_run_1.csv')
df_rating = df_rating %>% 
  filter(condition == 'interesting') %>% 
  select(towerID, button_pressed,prolificID)
df_rating$button_pressed = df_rating$button_pressed+1
df_rating_avg = df_rating %>% 
  group_by(towerID) %>% 
  summarise(mu = mean(button_pressed),
            sd = sd(button_pressed),
            n = n(),
            std_err = sd/sqrt(n))

df_towers = read_csv('curiobaby-cooltower-annotations.csv')

df_towers$towerID = df_towers$SID
df_towers = df_towers %>%  
  select(towerID, height_tallest)
df_full = merge(df_rating_avg,df_towers,by=c("towerID"))
glimpse(df_full)
df_full$height_tallest[is.na(df_full$height_tallest)] <- 1



ggplot(data = df_full, aes(x = height_tallest, y = mu))+ 
  geom_point(color = primary_color, size = 6)+
  geom_smooth(method = 'lm', color = secondary_color)+
  ylab('interesting')+
  xlab('tower height')+
  theme_update(# axis labels
    axis.title = element_text(size = 28))


df_rating_height = merge(df_rating,df_towers,by=c("towerID"))
model_height = lmer(button_pressed ~
                height_tallest+
                (1|towerID)+
                (1|prolificID),data=df_rating_height)
summary(model_height)
             