import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

interface ProcessingTypeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const processingTypes = [
  { value: "grayscale", label: "Grayscale" },
  { value: "blur", label: "Gaussian Blur" },
  { value: "edge_detection", label: "Edge Detection" },
  { value: "sharpen", label: "Sharpen" },
  { value: "invert", label: "Invert Colors" },
  { value: "sepia", label: "Sepia Tone" },
  { value: "brightness", label: "Brightness Adjustment" },
  { value: "contrast", label: "Contrast Enhancement" },
];

export const ProcessingTypeSelector = ({ value, onChange }: ProcessingTypeSelectorProps) => {
  return (
    <div className="space-y-2">
      <Label htmlFor="processing-type" className="text-sm font-medium">
        Processing Type
      </Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger 
          id="processing-type"
          className="w-full bg-card border-border shadow-sm hover:border-primary/50 transition-colors"
        >
          <SelectValue placeholder="Select processing type" />
        </SelectTrigger>
        <SelectContent className="bg-popover border-border shadow-lg z-50">
          {processingTypes.map((type) => (
            <SelectItem 
              key={type.value} 
              value={type.value}
              className="cursor-pointer hover:bg-accent focus:bg-accent"
            >
              {type.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
