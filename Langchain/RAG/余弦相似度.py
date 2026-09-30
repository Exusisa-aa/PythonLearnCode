import numpy
def get_dot(vec_a, vec_b):
    """
    计算两个向量的点积
    :param vec_a: 向量 a
    :param vec_b: 向量 b
    :return: 两个向量的点积
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("两个向量的维度不一致")
    dot_sum = 0
    for a, b in zip(vec_a, vec_b):
        dot_sum += a * b
    return dot_sum

def get_norm(vec):
    """
    计算单个向量的模长：对向量的每个数字求平方之和再开根号
    :param vec: 向量
    :return: 向量的模
    """
    sum_square = 0
    for v in vec:
        sum_square += v*v
    return numpy.sqrt(sum_square)

def cosine_similarity(vec_a, vec_b):
    """
    计算两个向量的余弦相似度
    :param vec_a: 向量 a
    :param vec_b: 向量 b
    :return: 两个向量的余弦相似度:两个向量的点积/两个向量模长的乘积
    """
    return get_dot(vec_a, vec_b) / (get_norm(vec_a) * get_norm(vec_b))


if __name__ == '__main__':
    vec_a = [0.5,0.5,0.5]
    vec_b = [0.7,0.7,0.7]
    vec_c = [0.7,0.5,0.5]
    vec_d = [-0.6,-0.5,-0.5]
    print("ab:",cosine_similarity(vec_a, vec_b))
    print("ac:",cosine_similarity(vec_a, vec_c))
    print("ad:",cosine_similarity(vec_a, vec_d))