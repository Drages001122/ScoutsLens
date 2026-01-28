<template>
  <div class="login-container">
    <div class="login-form">
      <h2 v-if="!showRegisterForm">用户登录</h2>
      
      <!-- 错误提示 -->
      <div v-if="errorMessage && !showRegisterForm" class="error-message">
        {{ errorMessage }}
      </div>
      
      <!-- 登录表单 -->
      <form v-if="!showRegisterForm" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required 
            placeholder="请输入用户名"
          >
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="请输入密码"
          >
        </div>
        
        <div class="form-actions">
          <button type="submit" class="login-button" :disabled="isLoading">
            {{ isLoading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
      
      <!-- 注册链接 -->
      <div v-if="!showRegisterForm" class="register-link">
        还没有账号？
        <button class="register-button" @click="showRegisterForm = true">
          立即注册
        </button>
      </div>
      
      <!-- 注册表单 -->
      <form v-if="showRegisterForm" @submit.prevent="handleRegister" class="register-form">
        <h2>用户注册</h2>
        
        <!-- 注册错误提示 -->
        <div v-if="registerErrorMessage" class="error-message">
          {{ registerErrorMessage }}
        </div>
        
        <div class="form-group">
          <label for="register-username">用户名</label>
          <input 
            type="text" 
            id="register-username" 
            v-model="registerUsername" 
            required 
            placeholder="请输入用户名"
          >
        </div>
        
        <div class="form-group">
          <label for="register-password">密码</label>
          <input 
            type="password" 
            id="register-password" 
            v-model="registerPassword" 
            required 
            placeholder="请输入密码"
          >
        </div>
        
        <div class="form-group">
          <label for="register-confirm-password">确认密码</label>
          <input 
            type="password" 
            id="register-confirm-password" 
            v-model="registerConfirmPassword" 
            required 
            placeholder="请再次输入密码"
          >
        </div>
        
        <div class="form-actions">
          <button type="submit" class="register-submit-button" :disabled="isRegisterLoading">
            {{ isRegisterLoading ? '注册中...' : '注册' }}
          </button>
        </div>
        
        <!-- 返回登录链接 -->
        <div class="back-to-login-link">
          已有账号？
          <button class="back-to-login-button" @click="showRegisterForm = false">
            返回登录
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      // 登录表单数据
      username: '',
      password: '',
      errorMessage: '',
      isLoading: false,
      
      // 注册表单数据
      showRegisterForm: false,
      registerUsername: '',
      registerPassword: '',
      registerConfirmPassword: '',
      registerErrorMessage: '',
      isRegisterLoading: false
    }
  },
  methods: {
    async handleLogin() {
      this.errorMessage = ''
      this.isLoading = true
      
      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          // 保存token和用户信息到本地存储
          localStorage.setItem('token', data.token)
          localStorage.setItem('user', JSON.stringify(data.user))
          
          // 登录成功后跳转到首页
          this.$router.push('/team-selection')
        } else {
          this.errorMessage = data.error || '登录失败'
        }
      } catch (error) {
        this.errorMessage = '网络错误，请稍后重试'
        console.error('登录错误:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async handleRegister() {
      this.registerErrorMessage = ''
      this.isRegisterLoading = true
      
      try {
        const response = await fetch('http://localhost:5000/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.registerUsername,
            password: this.registerPassword,
            confirm_password: this.registerConfirmPassword
          })
        })
        
        const data = await response.json()
        
        if (response.ok) {
          // 注册成功后自动登录
          localStorage.setItem('token', data.token)
          localStorage.setItem('user', JSON.stringify(data.user))
          
          // 跳转到首页
          this.$router.push('/team-selection')
        } else {
          this.registerErrorMessage = data.error || '注册失败'
        }
      } catch (error) {
        this.registerErrorMessage = '网络错误，请稍后重试'
        console.error('注册错误:', error)
      } finally {
        this.isRegisterLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-form {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
  width: 100%;
  max-width: 400px;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

h3 {
  margin-top: 20px;
  margin-bottom: 15px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-actions {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #45a049;
}

.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.register-link {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.register-button {
  background: none;
  border: none;
  color: #4CAF50;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  margin-left: 5px;
}

.register-button:hover {
  text-decoration: underline;
}

.register-submit-button {
  width: 100%;
  padding: 12px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-submit-button:hover {
  background-color: #1976D2;
}

.register-submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.back-to-login-link {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.back-to-login-button {
  background: none;
  border: none;
  color: #2196F3;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  margin-left: 5px;
}

.back-to-login-button:hover {
  text-decoration: underline;
}

.register-form {
  margin-top: 0;
  padding-top: 0;
}
</style>