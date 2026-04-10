<template>
  <div class="app-container p-4 md:p-6">
    <!-- github 角标 -->
    <github-corner class="github-corner" />

    <div class="glass-panel p-5">
      <div class="flex flex-wrap">
        <!-- 左侧问候语区域 -->
        <div class="flex-1 flex items-start">
          <img
            class="w-20 h-20 rounded-full"
            :src="userStore.userInfo.avatar + '?imageView2/1/w/80/h/80'"
          />
          <div class="ml-5">
            <p class="text-lg font-medium text-slate-700">{{ greetings }}</p>
          </div>
        </div>

        <!-- 右侧图标区域 - PC端 -->
        <div class="hidden sm:block">
          <div class="flex items-end space-x-6">
            <!-- 文档 -->
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

            <!-- 视频 -->
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

        <!-- 移动端图标区域 -->
        <div class="w-full sm:hidden mt-3">
          <div class="flex justify-end space-x-4 overflow-x-auto">
            <!-- 文档图标 -->
            <el-link href="" target="_blank">
              <div class="i-svg:juejin text-lg" />
            </el-link>
            <el-link href="" target="_blank">
              <div class="i-svg:csdn text-lg" />
            </el-link>
            <el-link href="" target="_blank">
              <div class="i-svg:cnblogs text-lg" />
            </el-link>

            <!-- 视频图标 -->
            <el-link href="" target="_blank">
              <div class="i-svg:bilibili text-lg" />
            </el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Dashboard",
  inheritAttrs: false,
});

// import { dayjs } from "element-plus";
// import LogAPI, { VisitStatsVO, VisitTrendVO } from "@/api/system/log-api";
import { useUserStore } from "@/store/modules/user-store";
// import { useTransition } from "@vueuse/core";
import { useOnlineCount } from "@/composables";

// 在线用户数量组件相关
const { onlineUserCount } = useOnlineCount();

// 记录上一次的用户数量用于计算趋势
const previousCount = ref(0);

// 监听用户数量变化，计算趋势
watch(onlineUserCount, (newCount, oldCount) => {
  if (oldCount > 0) {
    previousCount.value = oldCount;
  }
});

// // 格式化时间戳
// const formattedTime = computed(() => {
//   if (!lastUpdateTime.value) return "--";
//   return useDateFormat(lastUpdateTime.value, "HH:mm:ss").value;
// });

// interface VersionItem {
//   id: string;
//   title: string; // 版本标题（如：v2.4.0）
//   date: string; // 发布时间
//   content: string; // 版本描述
//   link: string; // 详情链接
//   tag?: string; // 版本标签（可选）
// }

const userStore = useUserStore();

// 当前通知公告列表
// const vesionList = ref<VersionItem[]>([
//   {
//     id: "1",
//     title: "v1.0.2",
//     date: "2025-10-06 00:00:00",
//     content: "布局重写，代码规范重构。",
//     link: "",
//     tag: "里程碑",
//   },
//   {
//     id: "2",
//     title: "v1.0.1",
//     date: "2025-10-01 00:00:00",
//     content: "vue2升级到vue3，包含新的组件库、新的路由系统等。",
//     link: "",
//     tag: "里程碑",
//   },
//   {
//     id: "3",
//     title: "v1.0.0",
//     date: "2025-09-01 00:00:00",
//     content: "实现基础框架搭建，包含权限管理、路由系统等核心功能。",
//     link: "",
//     tag: "里程碑",
//   },
// ]);

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

// 访客统计数据加载状态
// const visitStatsLoading = ref(true);
// // 访客统计数据
// const visitStatsData = ref<VisitStatsVO>({
//   todayUvCount: 0,
//   uvGrowthRate: 0,
//   totalUvCount: 0,
//   todayPvCount: 0,
//   pvGrowthRate: 0,
//   totalPvCount: 0,
// });

// 数字过渡动画
// const transitionUvCount = useTransition(
//   computed(() => visitStatsData.value.todayUvCount),
//   {
//     duration: 1000,
//     transition: [0.25, 0.1, 0.25, 1.0], // CSS cubic-bezier
//   }
// );

// const transitionTotalUvCount = useTransition(
//   computed(() => visitStatsData.value.totalUvCount),
//   {
//     duration: 1200,
//     transition: [0.25, 0.1, 0.25, 1.0],
//   }
// );
//
// const transitionPvCount = useTransition(
//   computed(() => visitStatsData.value.todayPvCount),
//   {
//     duration: 1000,
//     transition: [0.25, 0.1, 0.25, 1.0],
//   }
// );
//
// const transitionTotalPvCount = useTransition(
//   computed(() => visitStatsData.value.totalPvCount),
//   {
//     duration: 1200,
//     transition: [0.25, 0.1, 0.25, 1.0],
//   }
// );

// 访问趋势日期范围（单位：天）
const visitTrendDateRange = ref(7);
// 访问趋势图表配置
// const visitTrendChartOptions = ref();

/**
 * 获取访客统计数据
 */
// const fetchVisitStatsData = () => {
//   LogAPI.getVisitStats()
//     .then((data) => {
//       visitStatsData.value = data;
//     })
//     .finally(() => {
//       visitStatsLoading.value = false;
//     });
// };
//
// /**
//  * 获取访问趋势数据，并更新图表配置
//  */
// const fetchVisitTrendData = () => {
//   const startDate = dayjs()
//     .subtract(visitTrendDateRange.value - 1, "day")
//     .toDate();
//   const endDate = new Date();
//
//   LogAPI.getVisitTrend({
//     startDate: dayjs(startDate).format("YYYY-MM-DD"),
//     endDate: dayjs(endDate).format("YYYY-MM-DD"),
//   }).then((data) => {
//     updateVisitTrendChartOptions(data);
//   });
// };

/**
 * 更新访问趋势图表的配置项
 *
 * @param data - 访问趋势数据
 */
// const updateVisitTrendChartOptions = (data: VisitTrendVO) => {
//   visitTrendChartOptions.value = {
//     tooltip: {
//       trigger: "axis",
//     },
//     legend: {
//       data: ["浏览量(PV)", "访客数(UV)"],
//       bottom: 0,
//     },
//     grid: {
//       left: "1%",
//       right: "5%",
//       bottom: "10%",
//       containLabel: true,
//     },
//     xAxis: {
//       type: "category",
//       data: data.dates,
//     },
//     yAxis: {
//       type: "value",
//       splitLine: {
//         show: true,
//         lineStyle: {
//           type: "dashed",
//         },
//       },
//     },
//     series: [
//       {
//         name: "浏览量(PV)",
//         type: "line",
//         data: data.pvList,
//         areaStyle: {
//           color: "rgba(64, 158, 255, 0.1)",
//         },
//         smooth: true,
//         itemStyle: {
//           color: "#4080FF",
//         },
//         lineStyle: {
//           color: "#4080FF",
//         },
//       },
//       {
//         name: "访客数(UV)",
//         type: "line",
//         data: data.ipList,
//         areaStyle: {
//           color: "rgba(103, 194, 58, 0.1)",
//         },
//         smooth: true,
//         itemStyle: {
//           color: "#67C23A",
//         },
//         lineStyle: {
//           color: "#67C23A",
//         },
//       },
//     ],
//   };
// };

/**
 * 根据增长率计算对应的 CSS 类名
 *
 * @param growthRate - 增长率数值
 */
// const computeGrowthRateClass = (growthRate?: number): string => {
//   if (!growthRate) {
//     return "text-[--el-color-info]";
//   }
//   if (growthRate > 0) {
//     return "text-[--el-color-danger]";
//   } else if (growthRate < 0) {
//     return "text-[--el-color-success]";
//   } else {
//     return "text-[--el-color-info]";
//   }
// };

// 监听访问趋势日期范围的变化，重新获取趋势数据
watch(
  () => visitTrendDateRange.value,
  () => {
    // fetchVisitTrendData();
  },
  { immediate: true }
);

// 组件挂载后加载访客统计数据和通知公告数据
onMounted(() => {
  // fetchVisitStatsData();
});
</script>

<style lang="scss" scoped>
@use "@/styles/pages/dashboard";
</style>
