def ModelIt(data_from_sql, ucase, data_dri, patient, bad_foods):
    import sys
    sys.path.append('/usr/local/lib/python2.7/dist-packages/Numberjack/solvers')
    sys.path.append('/home/eileen/anaconda2/envs/my_projects_env/lib/python2.7/site-packages/Numberjack/solvers')
    sys.path.append('/home/eileen/anaconda2/envs/my_projects_env/lib/python2.7/site-packages/')
    import numpy as np
    import Numberjack as nj
    from SCIP import Solver
    import pandas as pd

    a=bad_foods.split()
    a=set(a)
    def check_word(row):
        return row['pos'] not in a
    data_from_sql=data_from_sql[data_from_sql.apply(check_word, axis=1)]


    nutrients=(100*np.array([data_from_sql['energy'],data_from_sql['carbs'],data_from_sql['protein'],data_from_sql['iron'],data_from_sql['vit_a'],data_from_sql['vit_c']])).astype(np.int)
    costs=(100*np.array(data_from_sql['price_serv'])).astype(np.int)
    ucase=int(ucase)
    #n=[100*ucase+500,100*100,100*30,100*6,100*625,100*75] #temporarily correct for buggy list above
    #ucase=int(ucase)
    n=[int(data_dri['energy'][ucase]), int(data_dri['carbs'][ucase]), int(data_dri['protein'][ucase]), int(data_dri['iron'][ucase]), int(data_dri['vit_a'][ucase]), int(data_dri['vit_c'][ucase])]
    
    patient=int(patient)

# Somewhat general definition of knapsack.
    def knapsack(costs, nutrients, n, patient):
        z = nj.Variable(patient, 10000)
        x = nj.VarArray(len(costs), 0, 1)
        model = nj.Model(
#            (z >= patient) & (z <= 950),
            #z >= patient,

            z == nj.Sum(x, costs),
            (nj.Sum(x, nutrients[0]) >= n[0]) & (nj.Sum(x, nutrients[0]) <= 250000), #nutrient #1
            (nj.Sum(x, nutrients[1]) >= n[1]) & (nj.Sum(x, nutrients[1]) <= 20000), #nutrient #2
            (nj.Sum(x, nutrients[2]) >= n[2]) & (nj.Sum(x, nutrients[2]) <= 10000), #nutrient #3
            (nj.Sum(x, nutrients[3]) >= n[3]) & (nj.Sum(x, nutrients[3]) <= 1100), #nutrient #4
            (nj.Sum(x, nutrients[4]) >= n[4]) & (nj.Sum(x, nutrients[4]) <= 200000), #nutrient #5
            (nj.Sum(x, nutrients[5]) >= n[5]) & (nj.Sum(x, nutrients[5]) <= 10000), #nutrient #6
            #nj.Sum(x)<=20,
            nj.Minimise(z)
            )
        return [model, x, z]
    
    
    def knapsack_model(libs, costs, nutrients, n, patient):
        [model, x, z] = knapsack(costs, nutrients, n, patient)
        for library in libs:
            solver = model.load(library)
            print ''
            if solver.solve():
                print "z: ", z
                print "x: ", x
                solver.printStatistics()
                print 'Nodes:', solver.getNodes(), ' Time:', solver.getTime()

            else:
                print "No solution"
                x=0
            print ''
        return x


    x=knapsack_model(['SCIP'], costs, nutrients, n, patient)


    #Create my_message DF with only foods to buy and their quantity
    numberjack_quants=np.zeros((len(x), 1))
    for item in range(len(x)):
        numberjack_quants[item]=int(str(x[item]))
    data_from_sql['num_serving']=numberjack_quants
    my_message=data_from_sql[numberjack_quants>0]

    births = []
    for i in range(0,my_message.shape[0]):
        births.append(dict(pos=my_message.iloc[i]['description'], quantity=my_message.iloc[i]['num_serving']*my_message.iloc[i]['serv_value'], serving=my_message.iloc[i]['serv_unit'], energy=my_message.iloc[i]['energy'], price_serv="{0:.2f}".format(my_message.iloc[i]['num_serving']*my_message.iloc[i]['price_serv'])))

    total_cost="{0:.02f}".format(sum(my_message['price_serv']))
    
    for i in range(0,my_message.shape[0]):
        my_message.iloc[i][['energy','carbs','protein','iron','vit_a','vit_c']]=my_message.iloc[i][['energy','carbs','protein','iron','vit_a','vit_c']]*my_message.iloc[i]['num_serving']


    #Table #2
    total_nutrients=[]
    total_nutrients.append(dict(energy=sum(my_message['energy']), carbs=sum(my_message['carbs']), protein=sum(my_message['protein']), iron=sum(my_message['iron']), vit_a=sum(my_message['vit_a']),vit_c=sum(my_message['vit_c'])))

    nutrients_dri=pd.DataFrame([2000,100,30,6,625,75],index=['energy','carbs','protein','iron','vit_a','vit_c'],columns=['dri'])
    nutrients_dri['yours']=[sum(my_message['energy']), sum(my_message['carbs']), sum(my_message['protein']), sum(my_message['iron']), sum(my_message['vit_a']),sum(my_message['vit_c'])]
    nutrients_dri['met']=nutrients_dri['yours']/nutrients_dri['dri']
    nutrients_dri['nname']=['Energy (kCal)','Carbohydrates (g)','Protein (g)', 'Iron (mg)', 'Vitamin A (IU)', 'Vitamin C (mg)']


    nutrients4=[]
    for i in range(0,nutrients_dri.shape[0]):
        nutrients4.append(dict(nname=nutrients_dri.iloc[i]['nname'],dri=nutrients_dri.iloc[i]['dri'], yours="{0:.0f}".format(nutrients_dri.iloc[i]['yours']), met="{0:.0%}".format(nutrients_dri.iloc[i]['met'])))
  


    return births, total_nutrients, nutrients4, total_cost
