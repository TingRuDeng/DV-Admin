/**
 * Element Plus internal icons use Vue object components as prop defaults.
 * Wrapping Lucide's functional components prevents Vue from invoking them as
 * default-value factories before a render context exists.
 */
import { defineComponent, h, type Component } from "vue";
import {
  ArrowDownWideNarrow as ArrowDownWideNarrowIcon,
  ArrowLeft as ArrowLeftIcon,
  ArrowRight as ArrowRightIcon,
  ArrowUp as ArrowUpIcon,
  ArrowUpWideNarrow as ArrowUpWideNarrowIcon,
  CalendarDays as CalendarDaysIcon,
  Check as CheckIcon,
  ChevronDown as ChevronDownIcon,
  ChevronRight as ChevronRightIcon,
  ChevronUp as ChevronUpIcon,
  ChevronsLeft as ChevronsLeftIcon,
  ChevronsRight as ChevronsRightIcon,
  CircleCheck as CircleCheckIcon,
  CircleHelp as CircleHelpIcon,
  CircleX as CircleXIcon,
  Clock as ClockIcon,
  Eye as EyeIcon,
  EyeOff as EyeOffIcon,
  FileText as FileTextIcon,
  Image as ImageIcon,
  Info as InfoIcon,
  LoaderCircle as LoaderCircleIcon,
  Maximize2 as Maximize2Icon,
  Minus as MinusIcon,
  MoreHorizontal as MoreHorizontalIcon,
  Plus as PlusIcon,
  RefreshCw as RefreshCwIcon,
  ScanLine as ScanLineIcon,
  Search as SearchIcon,
  Star as StarIcon,
  Trash2 as Trash2Icon,
  TriangleAlert as TriangleAlertIcon,
  X as XIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
} from "@lucide/vue";

function elementIcon(icon: Component) {
  return defineComponent({
    inheritAttrs: false,
    setup(_, { attrs }) {
      return () => h(icon, { "aria-hidden": true, ...attrs });
    },
  });
}

export const ArrowDown = elementIcon(ChevronDownIcon);
export const ArrowLeft = elementIcon(ArrowLeftIcon);
export const ArrowRight = elementIcon(ArrowRightIcon);
export const ArrowUp = elementIcon(ArrowUpIcon);
export const Back = elementIcon(ArrowLeftIcon);
export const Calendar = elementIcon(CalendarDaysIcon);
export const CaretRight = elementIcon(ChevronRightIcon);
export const CaretTop = elementIcon(ChevronUpIcon);
export const Check = elementIcon(CheckIcon);
export const CircleCheck = elementIcon(CircleCheckIcon);
export const CircleCheckFilled = elementIcon(CircleCheckIcon);
export const CircleClose = elementIcon(CircleXIcon);
export const CircleCloseFilled = elementIcon(CircleXIcon);
export const Clock = elementIcon(ClockIcon);
export const Close = elementIcon(XIcon);
export const DArrowLeft = elementIcon(ChevronsLeftIcon);
export const DArrowRight = elementIcon(ChevronsRightIcon);
export const Delete = elementIcon(Trash2Icon);
export const Document = elementIcon(FileTextIcon);
export const FullScreen = elementIcon(Maximize2Icon);
export const Hide = elementIcon(EyeOffIcon);
export const InfoFilled = elementIcon(InfoIcon);
export const Loading = elementIcon(LoaderCircleIcon);
export const Minus = elementIcon(MinusIcon);
export const More = elementIcon(MoreHorizontalIcon);
export const MoreFilled = elementIcon(MoreHorizontalIcon);
export const Image = elementIcon(ImageIcon);
export const QuestionFilled = elementIcon(CircleHelpIcon);
export const RefreshLeft = elementIcon(RefreshCwIcon);
export const RefreshRight = elementIcon(RefreshCwIcon);
export const ScaleToOriginal = elementIcon(ScanLineIcon);
export const Search = elementIcon(SearchIcon);
export const SortDown = elementIcon(ArrowDownWideNarrowIcon);
export const SortUp = elementIcon(ArrowUpWideNarrowIcon);
export const Star = elementIcon(StarIcon);
export const StarFilled = elementIcon(StarIcon);
export const SuccessFilled = elementIcon(CircleCheckIcon);
export const Eye = elementIcon(EyeIcon);
export const View = elementIcon(EyeIcon);
export const PictureFilled = elementIcon(ImageIcon);
export const WarningFilled = elementIcon(TriangleAlertIcon);
export const ZoomIn = elementIcon(ZoomInIcon);
export const ZoomOut = elementIcon(ZoomOutIcon);
export const Plus = elementIcon(PlusIcon);
