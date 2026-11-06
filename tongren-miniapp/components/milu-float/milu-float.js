/**
 * 悬浮 AI 人物「咪噜」
 * - 整体 scale(0.57) 小巧可爱，比之前 0.6 小 ~5px
 * - bottom 由组件根据 tab-bar 高度 + safe area + 空隙 自动算出，贴在 tab-bar 正上方
 * - 动作：微微跳动 bounce + 呼吸 idle + 点击小跳
 */
Component({
  properties: {
    /** 额外的上方偏移（px），默认 0；组件会自动加上 tab-bar + safe area */
    offsetTop: { type: Number, value: 0 },
    autoLoop: { type: Boolean, value: true }
  },

  data: {
    actClass: 'act-idle',
    showTip: true,
    bottomPx: 0
  },

  lifetimes: {
    attached() {
      // 根据 tab-bar 高度 + safe area 算 bottom，让咪噜刚好贴在 tab-bar 上方不被遮挡
      const info = wx.getSystemInfoSync();
      const safeBottomPx = (info.safeAreaInsets && info.safeAreaInsets.bottom) || 0;
      const tabBarPx = 150;    // tab-bar 内容区高度，保守值
      const gapPx = 8;        // 和 tab-bar 之间留 8px 空隙
      const bottomPx = tabBarPx + safeBottomPx + gapPx + (this.data.offsetTop || 0);
      this.setData({ bottomPx });

      this._tipTimer = setTimeout(() => { this.setData({ showTip: false }); }, 3200);
      if (this.data.autoLoop) this._nextAction();
    },
    detached() { this._clearTimers(); }
  },

  pageLifetimes: {
    hide() { this._clearTimers(); },
    show() { if (this.data.autoLoop) this._nextAction(); }
  },

  methods: {
    _clearTimers() {
      ['_tipTimer', '_loopTimer', '_resetTimer'].forEach((k) => {
        if (this[k]) clearTimeout(this[k]);
        this[k] = null;
      });
    },

    _nextAction() {
      if (this._loopTimer) clearTimeout(this._loopTimer);
      const delay = 3500 + Math.floor(Math.random() * 2500);
      this._loopTimer = setTimeout(() => {
        this.setData({ actClass: 'act-bounce' });
        this._resetTimer = setTimeout(() => {
          this.setData({ actClass: 'act-idle' });
          this._nextAction();
        }, 950);
      }, delay);
    },

    onTap() {
      this._clearTimers();
      this.setData({ actClass: 'act-jump', showTip: false });
      setTimeout(() => {
        this.setData({ actClass: 'act-idle' });
        this._nextAction();
      }, 500);

      const app = getApp();
      if (app && app.track) app.track('milu_open');
      wx.navigateTo({
        url: '/pages/ai/ai',
        fail() { wx.showToast({ title: '页面打开失败', icon: 'none' }); }
      });
    }
  }
});
