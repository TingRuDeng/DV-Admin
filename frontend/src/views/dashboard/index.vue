<template>
  <PageShell>
    <section class="ff-page-shell__hero ff-page-shell__hero--dashboard">
      <GithubCorner class="github-corner" />

      <div class="ff-dashboard__top">
        <div class="ff-dashboard__greeting">
          <img
            class="ff-dashboard__avatar"
            :src="userStore.userInfo.avatar + '?imageView2/1/w/80/h/80'"
          />
          <div class="ff-dashboard__copy">
            <p class="ff-dashboard__headline">{{ greetings }}</p>
          </div>
        </div>

        <div class="ff-dashboard__links hidden sm:block">
          <div class="flex items-end space-x-6">
            <div>
              <div class="font-bold color-#4080ff text-sm flex items-center">
                <el-icon class="mr-2px"><Document /></el-icon>
                文档
              </div>
              <div class="mt-3 whitespace-nowrap">
                <el-link href="" target="_blank">
                  <div class="i-svg:juejin text-lg" />
                </el-link>
                <el-divider direction="vertical" />
                <el-link href="" target="_blank">
                  <div class="i-svg:csdn text-lg" />
                </el-link>
                <el-divider direction="vertical" />
                <el-link href="" target="_blank">
                  <div class="i-svg:cnblogs text-lg" />
                </el-link>
              </div>
            </div>
            <div>
              <div class="font-bold color-#f76560 text-sm flex items-center">
                <el-icon class="mr-2px"><VideoCamera /></el-icon>
                视频
              </div>
              <div class="mt-3 whitespace-nowrap">
                <el-link href="" target="_blank">
                  <div class="i-svg:bilibili text-lg" />
                </el-link>
              </div>
            </div>
          </div>
        </div>

        <div class="ff-dashboard__mobile-links w-full sm:hidden mt-3">
          <div class="flex justify-end space-x-4 overflow-x-auto">
            <el-link href="" target="_blank">
              <div class="i-svg:juejin text-lg" />
            </el-link>
            <el-link href="" target="_blank">
              <div class="i-svg:csdn text-lg" />
            </el-link>
            <el-link href="" target="_blank">
              <div class="i-svg:cnblogs text-lg" />
            </el-link>
            <el-link href="" target="_blank">
              <div class="i-svg:bilibili text-lg" />
            </el-link>
          </div>
        </div>
      </div>
    </section>
  </PageShell>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dashboard",
  inheritAttrs: false,
});

import PageShell from "@/components/PageShell/index.vue";
import GithubCorner from "@/components/GithubCorner/index.vue";
import { useUserStore } from "@/store/modules/user-store";

const userStore = useUserStore();

// 当前时间（用于计算问候语）
const currentDate = new Date();

// 问候语：根据当前小时返回不同问候语
const greetings = computed(() => {
  const hours = currentDate.getHours();
  const name = userStore.userInfo.name;
  if (hours >= 6 && hours < 8) {
    return "晨起披衣出草堂，轩窗已自喜微凉🌅！";
  } else if (hours >= 8 && hours < 12) {
    return `上午好，${name}！`;
  } else if (hours >= 12 && hours < 18) {
    return `下午好，${name}！`;
  } else if (hours >= 18 && hours < 24) {
    return `晚上好，${name}！`;
  } else {
    return "偷偷向银河要了一把碎星，只等你闭上眼睛撒入你的梦中，晚安🌛！";
  }
});
</script>
