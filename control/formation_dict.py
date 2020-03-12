import numpy as np
formation_dict = {"cube": np.array([[1,1,1],[1,1,-1],[1,-1,-1],[1,-1,1],[-1,1,1],[-1,1,-1],[-1,-1,-1],[-1,-1,1]]), "pyramid": np.array([[1,1,-2],[1,-1,-2],[-1,-1,-2],[-1,1,-2],[2,2,-4],[2,-2,-4],[-2,-2,-4],[-2,2,-4]]), "square": np.array([[0,1,1],[0,0,1],[0,-1,1],[0,1,0],[0,-1,0],[0,-1,-1],[0,0,-1],[0,1,-1]]),"waiting":np.zeros([3,9])}
formation_dict["cube"] = np.transpose(formation_dict["cube"])
formation_dict["pyramid"] = np.transpose(formation_dict["pyramid"])
formation_dict["square"] = np.transpose(formation_dict["square"])