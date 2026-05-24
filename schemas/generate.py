from pydantic import BaseModel, Field, model_validator


class GenerateRequest(BaseModel):
    # Garment design (exactly one required)
    garment_text: str | None = Field(default=None, max_length=200)
    garment_filename: str | None = None
    
    # Color (exactly one required)
    color_text: str | None = Field(default=None, max_length=200)
    color_filename: str | None = None
    
    # Fabric (exactly one required)
    fabric_text: str | None = Field(default=None, max_length=200)
    fabric_filename: str | None = None
    
    @model_validator(mode='after')
    def validate_inputs(self):
        garment_count = sum([
            bool(self.garment_text and self.garment_text.strip()),
            bool(self.garment_filename)
        ])
        if garment_count != 1:
            raise ValueError(
                'Please provide exactly one garment design input: '
                'either a text description or an uploaded image.'
            )
            
        color_count = sum([
            bool(self.color_text and self.color_text.strip()),
            bool(self.color_filename)
        ])
        if color_count != 1:
            raise ValueError(
                'Please provide exactly one color input: '
                'either a hex color code or an uploaded image.'
            )
            
        fabric_count = sum([
            bool(self.fabric_text and self.fabric_text.strip()),
            bool(self.fabric_filename)
        ])
        if fabric_count != 1:
            raise ValueError(
                'Please provide exactly one fabric input: '
                'either a text description or an uploaded image.'
            )
            
        return self
            
        