def ModelIt(data_from_sql):
    import sys
    sys.path.append('/usr/local/lib/python2.7/dist-packages/Numberjack/solvers')
    import numpy as np
    import Numberjack as nj
    from Mistral import Solver
    nutrients=(100*np.array([data_from_sql['energy'],data_from_sql['carbs'],data_from_sql['protein'],data_from_sql['iron'],data_from_sql['vit_a'],data_from_sql['vit_c']])).astype(np.int)
    costs=(100*np.array(data_from_sql['price_serv'])).astype(np.int)
    n=[100*2000,100*100,100*30,100*6,100*625,100*75] #temporarily correct for buggy list above
    #n=[data_dri['energy'],data_dri['carbs'],data_dri['protein'],data_dri['iron'],data_dri['vit_a'],data_dri['vit_c']]
        
    def knapsack(costs, nutrients, n):
        z = nj.Variable(0, 10000)
        x = nj.VarArray(len(costs), 0, 20)
        model = nj.Model(
            z >= 0,
            z == nj.Sum(x, costs),
            nj.Sum(x, nutrients[0]) >= n[0], #nutrient #1
            nj.Sum(x, nutrients[1]) >= n[1], #nutrient #2
            nj.Sum(x, nutrients[2]) >= n[2], #nutrient #3
            nj.Sum(x, nutrients[3]) >= n[3], #nutrient #4
            nj.Sum(x, nutrients[4]) >= n[4], #nutrient #5
            nj.Sum(x, nutrients[5]) >= n[5], #nutrient #6
            nj.Minimise(z)
            )
        return [model, x, z]
    
    
    def knapsack_model(libs, costs, nutrients, n):
        [model, x, z] = knapsack(costs, nutrients, n)
        #my_message='howdy'
        for library in libs:
            solver = model.load(library)
            print ''
            if solver.solve():
                print "z: ", z
                print "x: ", x
                solver.printStatistics()
                print 'Nodes:', solver.getNodes(), ' Time:', solver.getTime()
                #my_message= ' x:', str(x), ' z:', str(z)

            else:
                print "No solution"
                x=0
            print ''
        #my_message = x #' x:', str(x), ' z:', str(z)
        return x#my_message


    # knapsack_model(['SCIP'], values, weights, n)
    x=knapsack_model(['Mistral'], costs, nutrients, n)

    numberjack_quants=np.zeros((len(x), 1))
    for item in range(len(x)):
        numberjack_quants[item]=int(str(x[item]))
    data_from_sql['num_serving']=numberjack_quants
    my_message=data_from_sql[numberjack_quants>0]

    births = []
    for i in range(0,my_message.shape[0]):
        births.append(dict(pos=my_message.iloc[i]['pos'], quantity=my_message.iloc[i]['num_serving']*my_message.iloc[i]['serv_value'], serving=my_message.iloc[i]['serv_unit'], energy=my_message.iloc[i]['energy'], price_serv=my_message.iloc[i]['num_serving']*my_message.iloc[i]['price_serv']))
    
    for i in range(0,my_message.shape[0]):
        my_message.iloc[i][['energy','protein','carbs','vit_a']]=my_message.iloc[i][['energy','protein','carbs','vit_a']]*my_message.iloc[i]['num_serving']

    total_nutrients=[]
    total_nutrients.append(dict(energy=sum(my_message['energy']), carbs=sum(my_message['carbs']), protein=sum(my_message['protein']), iron=sum(my_message['iron']), vit_a=sum(my_message['vit_a']),vit_c=sum(my_message['vit_c'])))


    return births, total_nutrients
