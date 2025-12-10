#include <iostream>
#include <queue>
using namespace std;

// 二叉树节点结构
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

// 创建一棵简单的二叉树
TreeNode* buildTree() {
    /* 构造如下二叉树：
          1
         / \
        2   3
       / \   \
      4   5   6
    */
    TreeNode* root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    root->left->left = new TreeNode(4);
    root->left->right = new TreeNode(5);
    root->right->right = new TreeNode(6);
    
    return root;
}

// 前序遍历：根->左->右
void preorderTraversal(TreeNode* root) {
    if (root == nullptr) return;
    
    cout << root->val << " ";
    preorderTraversal(root->left);
    preorderTraversal(root->right);
}

// 中序遍历：左->根->右
void inorderTraversal(TreeNode* root) {
    if (root == nullptr) return;
    
    inorderTraversal(root->left);
    cout << root->val << " ";
    inorderTraversal(root->right);
}

// 后序遍历：左->右->根
void postorderTraversal(TreeNode* root) {
    if (root == nullptr) return;
    
    postorderTraversal(root->left);
    postorderTraversal(root->right);
    cout << root->val << " ";
}

// 广度优先遍历（层序遍历）
void breadthFirstTraversal(TreeNode* root) {
    if (root == nullptr) return;
    
    queue<TreeNode*> q;
    q.push(root);
    
    cout << "广度优先遍历: ";
    while (!q.empty()) {
        TreeNode* current = q.front();
        q.pop();
        cout << current->val << " ";
        
        // 将左右子节点加入队列
        if (current->left != nullptr) 
            q.push(current->left);
        if (current->right != nullptr) 
            q.push(current->right);
    }
    cout << endl;
}

// 带层级的广度优先遍历（显示每层的节点）
void levelOrderWithLevels(TreeNode* root) {
    if (root == nullptr) return;
    
    queue<TreeNode*> q;
    q.push(root);
    
    cout << "带层级的广度优先遍历:" << endl;
    int level = 0;
    
    while (!q.empty()) {
        int levelSize = q.size();
        cout << "第 " << level << " 层: ";
        
        for (int i = 0; i < levelSize; i++) {
            TreeNode* current = q.front();
            q.pop();
            cout << current->val << " ";
            
            if (current->left != nullptr) 
                q.push(current->left);
            if (current->right != nullptr) 
                q.push(current->right);
        }
        cout << endl;
        level++;
    }
}

int main() {
    TreeNode* root = buildTree();
    
    cout << "前序遍历: ";
    preorderTraversal(root);
    cout << endl;
    
    cout << "中序遍历: ";
    inorderTraversal(root);
    cout << endl;
    
    cout << "后序遍历: ";
    postorderTraversal(root);
    cout << endl;
    
    breadthFirstTraversal(root);
    levelOrderWithLevels(root);
    
    return 0;
}
