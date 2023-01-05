# resources_README

## For starters
If you’re new to terms like machine learning and neural networks it might be helpful to first go through this video: https://www.youtube.com/watch?v=aircAruvnKk

Also feel free to check the rest of their videos, it’s an awesome channel!

Feel free to bypass any of the following bullet points if you’re already familiar with it ;)

However, if you’re not familiar with any of these next terms, google what they mean and maybe watch a youtube introductory video to get started:

- Jupyter notebooks

- Github/Git

- Cloning a repository from Github


## Setting-up your computing environment
Unfortunately, for every project/tutorial you work through, you first have to setup a computing environment. As you might suspect, each project requires specific packages (ex: numpy, pandas, .. ) and even specific versions of these packages. This imposes an obstacle when you want to experiment with different tutorials.

There are several ways to setup these packages, we share a few below:

**(1) Using google colab**

**Pro**: you don’t have to worry about installing packages yourself because most packages are already pre-installed. And even if you can’t find a package, you can just run the following command in a cell:

    !pip install <name_of_package>

**Cons**: you need a stable wifi connection.. you need to be living outside of china.. might/should not be a convenient option when you start developing your own projects

**(2) Using conda (recommended)**

First, Familiarize yourself with conda: https://conda.io/projects/conda/en/latest/user-guide/getting-started.html

Once you have anaconda installed on your machine, you can start creating computing environments. Usually, a “good” github repository that contains a jupyter notebook tutorial should contain a file “requirements.txt” which contains all the necessary computing packages. You can then google how to create a conda environment using this “requirements.txt” file.

Once you create the conda enviornment, activate it and then launch the jupuyter notebook tutorial (google how if you don't know) and work through it.

**(3) Using docker containers**

Google what it means :)
