import cPickle
import logging
import csv

logging.basicConfig(level=logging.INFO)

# with open('temp_data.pkl','rb') as f:
# 	data = cPickle.load(f)
# 	logging.info("Loaded temp results file")
# # with open('temp_users.pkl','rb') as f:
# # 	users = cPickle.load(f)
# # 	logging.info("Loaded temp results file")

# for d in data:
# 	d[5] = d[5].rstrip('\n')

# logging.info(len(data))

# with open('data2.csv','w') as f2:
# 	datawriter = csv.writer(f2, delimiter=',')
# 	datawriter.writerows(data)


sentences = []
with open('data.csv','r') as f:
	reader = csv.reader(f,delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	for row in reader:
		sentences.append(row)

for sentence in sentences:
	logging.info(sentence[5])
	sentence[5] = sentence[5].rstrip('\n')

with open('cleaned.csv','wb') as f:
	csvwriter = csv.writer(f,delimiter=',')
	csvwriter.writerows(sentences)

logging.info(len(sentences))