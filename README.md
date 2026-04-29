1. If you are not on linux, then you will need to either setup a VM or get WSL for windows (https://learn.microsoft.com/en-us/windows/wsl/install).
2. run wget on linux http://plse.cs.washington.edu/daikon/download/daikon-5.8.22.tar.gz to get Daikon
3. run tar zxf daikon-5.8.22.tar.gz
4. run 
    export DAIKONDIR=/path/to/daikon-5.8.22
    export CLASSPATH=$CLASSPATH:$DAIKONDIR/daikon.jar
5. Daikon should be downloaded. Change to the software_analysis_project directory.
6. Run javac -g project/*.java
7. Run mkdir data
8. Run these 4 commands.
    java daikon.Chicory --ppt-select-pattern="pop_stack" --nesting-depth=2 --std-visibility project.pop_data
    java daikon.Chicory --ppt-select-pattern="push_stack" --nesting-depth=2 --std-visibility project.push_data
    java daikon.Chicory --ppt-select-pattern="proj_motion_simulator" --nesting-depth=2 --std-visibility project.projectile_data
    java daikon.Chicory --ppt-select-pattern="triangle_classifier" --nesting-depth=2 --std-visibility project.triangle_data
9. Run these 4 commands. I copied and pasted the invariant output into .txt files for later use, but you don't need to.
    java daikon.Daikon pop_data.dtrace.gz
    java daikon.Daikon push_data.dtrace.gz
    java daikon.Daikon projectile_data.dtrace.gz
    java daikon.Daikon triangle_data.dtrace.gz project/triangle.spinfo
10. Those commands should have generated the data and the Daikon invariants. The data should be in the data folder in the main directory.
11. Run these 4 commands in the main (software_analysis_project) folder
    mkdir pop_mutant
    mkdir push_mutant
    mkdir proj_mutant
    mkdir tri_mutant
12. Run the following java files to generate the mutant data
    java project.projectile_mutant_tester
    java project.push_mutant_tester
    java project.triangle_mutant_tester
    java project.pop_mutant_tester
13. Move the folders made in step 11 to the "mutants/" folder in the score_based_diff folder. You do not have to do this, as my data is already there.
14. Move the data folder to the score_based_diff folder. You do not have to do this, as my data is already there.
15. cd into the score_based_diff folder
16. Run mkdir threshold_flag_results
17. Now you can train diffusion models on each setup using the following commands. This will take 10-20 minutes on cpu, so I recommend using the models I already have. You can also go into the file and reduce the parameters such as the model size, epochs, or patience to make things quicker. I ran it with the defaults, though, so you could have worse results by changing params.
    python diffusion_scorebased_sde.py --experiment triangle --id 1 --sigma_max 1.0 --sigma_min 0.01
    python diffusion_scorebased_sde.py --experiment pop --id 2 --sigma_max 1.0 --sigma_min 0.01
    python diffusion_scorebased_sde.py --experiment push --id 3 --sigma_max 1.0 --sigma_min 0.01
    python diffusion_scorebased_sde.py --experiment projectile --id 4 --sigma_max 1.0 --sigma_min 0.01
18. You can now run these 8 commands to get the threshold flag rates. You will need to swap the ids to 1, 2, 3, and 4 if you trained your own models. The model ids here correspond to the models I trained already.
    python diffusion_mutant_tester.py --experiment projectile --id 300 --threshold_level p99.5
    python diffusion_mutant_tester.py --experiment projectile --id 300 --threshold_level p99
    python diffusion_mutant_tester.py --experiment triangle --id 303 --threshold_level p99.5 --sigma_min 0.001
    python diffusion_mutant_tester.py --experiment triangle --id 303 --threshold_level p99 --sigma_min 0.001
    python diffusion_mutant_tester.py --experiment push --id 302 --threshold_level p99.5
    python diffusion_mutant_tester.py --experiment push --id 302 --threshold_level p99
    python diffusion_mutant_tester.py --experiment pop --id 301 --threshold_level p99.5
    python diffusion_mutant_tester.py --experiment pop --id 301 --threshold_level p99
19. Now you can run the KS test files. My results are already saved, though.
    python diffusion_ks_mutant_tester.py --experiment projectile --id 300
    python diffusion_ks_mutant_tester.py --experiment push --id 302
    python diffusion_ks_mutant_tester.py --experiment pop --id 301
    python diffusion_ks_mutant_tester.py --experiment triangle --id 303 --sigma_min 0.001
20. I transformed the Daikon invariants into a Python file using an LLM. Just run these to get the Daikon results.
    python pop_rules.py
    python push_rules.py
    python projectile_rules.py
    python triangle_rules.py
21. Now you have the threshold results (step 18), the KS results (step 19), and the Daikon results (step 20). You are done.
