#include <iostream>
#include <api.h>
#include <tree.h>
#include <utils.h>

int main(){
    // fix (N,p)
    int N = 4;
    int p = 2;
    //inport databsase
    TreesApi db_in("trees.db", true);

    db_in.import_csv("Trees_1to7.csv");

    std::vector<Tree> local_vec = db_in.get_trees(N);

    //export database
    TreesApi db_out("physics_4", true);

    db_out.db.execute("CREATE TABLE IF NOT EXISTS physics_N4_p2(tree_id INTEGER NOT NULL, charges TEXT NOT NULL, term REAL),");

    //TODO: Save to table with p in the name 

    //Pick your charges, should be an array of size N.
    double charges[] = {1,1,1,1};
    //Create array of all the ineraction chargers
    std::vector<double> I_charges = interaction_energy(charges, N);

    //Grabs the e_i term
    double interaction_energy_I = I_charges[15];

    //Go through each beta and record all thse options. 
    for (int beta = 0; beta <= 10; beta ++ ){
        /*
        //Calculates Z_I
         double sum = 0.0; 
             for (Tree fork :local_vec){
             sum += fork.term(beta, p, I_charges);
              }
        double Z_4 = pow(p, interaction_energy_I * beta) * sum;
        */
        for(Tree fork : local_vec){
            if (beta ==0){
                //Insert the not physical probabilities to the table
                db_out.insert(fork.probability(p));
            }
            else{
                //Insert the term to the table
                //db_out.insert(fork.term(beta, p, I_charges));

                //OR

                //Insert the term multiplied by the gibbs measure
                //db_out.insert((pow(p,interaction_energy_I * beta)/Z_4)*fork.term(beta, p, I_charges));
            }
        }
    }


    return 0;
}