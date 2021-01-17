library(tidyverse)
library(lme4)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
dat = read_csv('curiotower_raw_data_run_0.csv')
glimpse(dat)
dat = dat %>% select('button_pressed',
                     'num_blocks',
                     'stability',
                     'viewpoint',
                     'towerID',
                     'prolificID')


#LME interestingness_rating ~ Jitter + Height + (1 | tower) + (1 | subjID)
model1 = lmer(button_pressed ~ 1 + 
               stability + 
               num_blocks +
               (1|towerID)+
               (1|prolificID),data=dat)
summary(model1)
anova(model1)

model2 = lmer(button_pressed ~ 1 + 
                stability * 
                num_blocks +
                (1|towerID)+
                (1|prolificID),data=dat)
summary(model2)
anova(model2)
#copmare model1 and model 2
anova(model1,model2)

model3 = lmer(button_pressed ~ 1 + 
                stability *
                num_blocks +
                viewpoint+
                (1|towerID)+
                (1|prolificID),data=dat)
summary(model3)
anova(model3)

anova(model2, model3)

