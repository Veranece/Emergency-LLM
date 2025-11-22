import { createStore } from 'vuex'
import axios from 'axios'

export default createStore({
  state: {
    chatHistory: [],
    isLoading: false,
    controller: null // 存储AbortController实例
  },
  mutations: {
    // 添加用户消息到历史记录
    ADD_USER_MESSAGE(state, message) {
      state.chatHistory.push({
        type: 'user',
        content: message
      })
    },
    // 添加机器人消息到历史记录
    ADD_ROBOT_MESSAGE(state, message) {
      state.chatHistory.push({
        type: 'robot',
        content: message
      })
    },
    // 更新最后一条机器人消息的内容
    UPDATE_LAST_ROBOT_MESSAGE(state, message) {
      const lastRobotIndex = [...state.chatHistory].reverse().findIndex(msg => msg.type === 'robot')
      if (lastRobotIndex !== -1) {
        state.chatHistory[state.chatHistory.length - 1 - lastRobotIndex].content = message
      }
    },
    // 设置加载状态
    SET_LOADING(state, isLoading) {
      state.isLoading = isLoading
    },
    // 设置控制器
    SET_CONTROLLER(state, controller) {
      state.controller = controller
    }
  },
  actions: {
    // 发送消息到服务器
    async sendMessage({ commit, state }, message) {
      // 添加用户消息到历史
      commit('ADD_USER_MESSAGE', message)
      
      // 设置加载状态
      commit('SET_LOADING', true)
      
      // 添加一条空的机器人消息
      commit('ADD_ROBOT_MESSAGE', '思考中...')
      
      // 创建AbortController实例
      const controller = new AbortController()
      commit('SET_CONTROLLER', controller)
      
      try {
        // 发送请求
        const response = await fetch('http://shizi.hzau.edu.cn:5888/getMessage', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json; charset=utf-8'
          },
          body: JSON.stringify({ userMessage: message }),
          signal: controller.signal
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`)
        }
        
        // 获取响应的可读流
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let fullText = ''
        
        // 读取流
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            break
          }
          
          // 解码收到的数据
          const chunk = decoder.decode(value, { stream: true })
          fullText += chunk
          
          // 更新机器人消息
          commit('UPDATE_LAST_ROBOT_MESSAGE', fullText)
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('请求被用户中止')
          commit('UPDATE_LAST_ROBOT_MESSAGE', fullText + '\n\n(已停止生成)')
        } else {
          console.error('请求失败:', error)
          commit('UPDATE_LAST_ROBOT_MESSAGE', '请求失败，请稍后再试')
        }
      } finally {
        // 重置状态
        commit('SET_LOADING', false)
        commit('SET_CONTROLLER', null)
      }
    },
    
    // 停止生成
    stopGeneration({ state, commit }) {
      if (state.controller) {
        state.controller.abort()
        commit('SET_CONTROLLER', null)
      }
    },
    
    // 搜索华农网站
    async searchHZAU({ commit }, keyword) {
      try {
        const searchData = {
          keyWord: keyword,
          owner: "2027508739",
          token: "tourist",
          urlPrefix: "/aop_component/",
          lang: "i18n_zh_CN"
        }
        
        const response = await axios.post('http://shizi.hzau.edu.cn:5888/proxy', searchData)
        
        if (response.data.redirect_url) {
          window.location.href = response.data.redirect_url
          return true
        } else {
          return false
        }
      } catch (error) {
        console.error('搜索失败:', error)
        return false
      }
    }
  },
  getters: {
    getChatHistory: state => state.chatHistory,
    isLoading: state => state.isLoading
  }
}) 